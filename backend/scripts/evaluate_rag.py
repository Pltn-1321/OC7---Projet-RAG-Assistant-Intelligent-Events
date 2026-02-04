#!/usr/bin/env python3
"""Script d'evaluation du systeme RAG avec RAGAS.

Ce script evalue la qualite du systeme RAG en utilisant:
- Des metriques personnalisees (latence, couverture des mots-cles)
- Le framework RAGAS (faithfulness, answer_relevancy, context_precision)

Usage:
    uv run python scripts/evaluate_rag.py
    uv run python scripts/evaluate_rag.py --skip-ragas  # Sans metriques RAGAS
    uv run python scripts/evaluate_rag.py --test-file tests/data/test_questions.json
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Ajouter le repertoire racine au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config.constants import PROCESSED_DATA_DIR
from src.data.models import EvaluationQuestion


def load_test_questions(filepath: Path) -> list[EvaluationQuestion]:
    """Charge les questions de test depuis un fichier JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [EvaluationQuestion(**q) for q in data]


def calculate_keyword_coverage(answer: str, expected_keywords: list[str]) -> dict:
    """Calcule la couverture des mots-cles dans la reponse."""
    if not expected_keywords:
        return {"keywords_found": 0, "keywords_total": 0, "coverage": 1.0}

    answer_lower = answer.lower()
    found = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)

    return {
        "keywords_found": found,
        "keywords_total": len(expected_keywords),
        "coverage": found / len(expected_keywords),
    }


def run_rag_queries(
    questions: list[EvaluationQuestion], top_k: int = 5
) -> list[dict]:
    """Execute les requetes RAG et collecte les resultats."""
    from src.rag.engine import RAGEngine

    print("\n" + "=" * 60)
    print("INITIALISATION")
    print("=" * 60)

    engine = RAGEngine()
    print(f"Index charge: {engine.num_documents} documents")
    print(f"Dimension embeddings: {engine.embedding_dim}")

    results = []

    print("\n" + "=" * 60)
    print(f"EXECUTION DES {len(questions)} REQUETES")
    print("=" * 60)

    for i, q in enumerate(questions, 1):
        print(f"\n[{i}/{len(questions)}] {q.question[:50]}...")

        start_time = time.time()

        # Executer la recherche
        search_results = engine.search(q.question, top_k=top_k)
        contexts = [r["document"]["content"] for r in search_results]

        # Generer la reponse
        chat_result = engine.chat(q.question, top_k=top_k)
        answer = chat_result["response"]
        used_rag = chat_result["used_rag"]

        latency = time.time() - start_time

        # Calculer les metriques
        keyword_metrics = calculate_keyword_coverage(answer, q.expected_keywords)

        result = {
            "question_id": q.id,
            "question": q.question,
            "category": q.category,
            "answer": answer,
            "contexts": contexts,
            "latency": latency,
            "used_rag": used_rag,
            "expected_keywords": q.expected_keywords,
            **keyword_metrics,
        }

        results.append(result)

        # Afficher les resultats intermediaires
        print(f"   Latence: {latency:.2f}s | RAG: {used_rag} | Keywords: {keyword_metrics['coverage']:.0%}")

    return results


def run_ragas_evaluation(results: list[dict]) -> dict:
    """Execute l'evaluation RAGAS sur les resultats collectes."""
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import (
            answer_relevancy,
            context_precision,
            context_recall,
            faithfulness,
        )
    except ImportError:
        print("\n[WARN] RAGAS non installe. Installez avec: uv sync --extra evaluation")
        return {}

    print("\n" + "=" * 60)
    print("EVALUATION RAGAS")
    print("=" * 60)
    print("Cela peut prendre plusieurs minutes...")

    # Filtrer les resultats avec contexte (uniquement ceux qui ont utilise RAG)
    rag_results = [r for r in results if r["used_rag"] and r["contexts"]]

    if not rag_results:
        print("[WARN] Aucun resultat avec contexte pour RAGAS")
        return {}

    # Preparer le dataset pour RAGAS
    dataset_dict = {
        "question": [r["question"] for r in rag_results],
        "answer": [r["answer"] for r in rag_results],
        "contexts": [r["contexts"] for r in rag_results],
        "ground_truth": [" ".join(r["expected_keywords"]) if r["expected_keywords"] else r["question"] for r in rag_results],
    }

    dataset = Dataset.from_dict(dataset_dict)

    # Executer l'evaluation RAGAS
    metrics = [
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ]

    try:
        ragas_results = evaluate(dataset, metrics=metrics)
        return dict(ragas_results)
    except Exception as e:
        print(f"[ERROR] Erreur RAGAS: {e}")
        return {}


def generate_report(
    results: list[dict],
    ragas_scores: dict,
    output_path: Path,
) -> dict:
    """Genere le rapport d'evaluation."""
    # Calculer les metriques agregees
    total_latency = sum(r["latency"] for r in results)
    avg_latency = total_latency / len(results)

    keyword_coverages = [r["coverage"] for r in results if r["expected_keywords"]]
    avg_keyword_coverage = sum(keyword_coverages) / len(keyword_coverages) if keyword_coverages else 1.0

    rag_used_count = sum(1 for r in results if r["used_rag"])
    conversation_count = len(results) - rag_used_count

    # Categoriser les resultats
    by_category = {}
    for r in results:
        cat = r["category"]
        if cat not in by_category:
            by_category[cat] = {"count": 0, "total_latency": 0, "total_coverage": 0}
        by_category[cat]["count"] += 1
        by_category[cat]["total_latency"] += r["latency"]
        by_category[cat]["total_coverage"] += r["coverage"]

    for cat, stats in by_category.items():
        stats["avg_latency"] = stats["total_latency"] / stats["count"]
        stats["avg_coverage"] = stats["total_coverage"] / stats["count"]

    report = {
        "timestamp": datetime.now().isoformat(),
        "num_questions": len(results),
        "aggregate_metrics": {
            "avg_latency_seconds": round(avg_latency, 3),
            "avg_keyword_coverage": round(avg_keyword_coverage, 3),
            "total_execution_time": round(total_latency, 2),
            "rag_queries": rag_used_count,
            "conversation_queries": conversation_count,
        },
        "ragas_scores": {
            k: round(v, 3) if isinstance(v, (int, float)) else v
            for k, v in ragas_scores.items()
        } if ragas_scores else {},
        "by_category": {
            cat: {
                "count": stats["count"],
                "avg_latency": round(stats["avg_latency"], 3),
                "avg_coverage": round(stats["avg_coverage"], 3),
            }
            for cat, stats in by_category.items()
        },
        "individual_results": [
            {
                "question_id": r["question_id"],
                "question": r["question"],
                "category": r["category"],
                "latency": round(r["latency"], 3),
                "used_rag": r["used_rag"],
                "keywords_found": r["keywords_found"],
                "keywords_total": r["keywords_total"],
                "coverage": round(r["coverage"], 3),
            }
            for r in results
        ],
    }

    # Sauvegarder le rapport
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return report


def print_summary(report: dict) -> None:
    """Affiche le resume de l'evaluation."""
    print("\n" + "=" * 60)
    print("RESUME DE L'EVALUATION")
    print("=" * 60)

    metrics = report["aggregate_metrics"]
    print(f"\nQuestions evaluees: {report['num_questions']}")
    print(f"  - Requetes RAG: {metrics['rag_queries']}")
    print(f"  - Conversations: {metrics['conversation_queries']}")

    print(f"\nPerformance:")
    print(f"  Latence moyenne: {metrics['avg_latency_seconds']:.2f}s")
    print(f"  Temps total: {metrics['total_execution_time']:.2f}s")

    print(f"\nQualite:")
    print(f"  Couverture mots-cles: {metrics['avg_keyword_coverage']:.1%}")

    if report["ragas_scores"]:
        print("\nScores RAGAS:")
        for metric, score in report["ragas_scores"].items():
            if isinstance(score, (int, float)):
                print(f"  {metric}: {score:.3f}")

    print("\nResultats par categorie:")
    for cat, stats in report["by_category"].items():
        print(f"  {cat}:")
        print(f"    Questions: {stats['count']}")
        print(f"    Latence moy.: {stats['avg_latency']:.2f}s")
        print(f"    Couverture: {stats['avg_coverage']:.1%}")


def main():
    parser = argparse.ArgumentParser(
        description="Evalue le systeme RAG avec RAGAS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  uv run python scripts/evaluate_rag.py
  uv run python scripts/evaluate_rag.py --skip-ragas
  uv run python scripts/evaluate_rag.py --test-file tests/data/custom_questions.json
        """,
    )
    parser.add_argument(
        "--test-file",
        type=Path,
        default=Path("tests/data/test_questions.json"),
        help="Chemin vers le fichier de questions de test (default: tests/data/test_questions.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROCESSED_DATA_DIR / "evaluation_results.json",
        help="Chemin du fichier de rapport (default: data/processed/evaluation_results.json)",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Nombre de documents a recuperer (default: 5)",
    )
    parser.add_argument(
        "--skip-ragas",
        action="store_true",
        help="Ignorer l'evaluation RAGAS (plus rapide)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("EVALUATION DU SYSTEME RAG")
    print("=" * 60)
    print(f"Fichier de questions: {args.test_file}")
    print(f"Fichier de sortie: {args.output}")
    print(f"Top-K: {args.top_k}")
    print(f"RAGAS: {'Desactive' if args.skip_ragas else 'Active'}")

    # Charger les questions
    if not args.test_file.exists():
        print(f"\n[ERROR] Fichier non trouve: {args.test_file}")
        sys.exit(1)

    questions = load_test_questions(args.test_file)
    print(f"\n{len(questions)} questions chargees")

    # Executer les requetes RAG
    try:
        results = run_rag_queries(questions, top_k=args.top_k)
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("Assurez-vous que l'index FAISS est construit.")
        sys.exit(1)

    # Evaluation RAGAS (optionnelle)
    ragas_scores = {}
    if not args.skip_ragas:
        ragas_scores = run_ragas_evaluation(results)

    # Generer le rapport
    report = generate_report(results, ragas_scores, args.output)

    # Afficher le resume
    print_summary(report)

    print(f"\nRapport complet: {args.output}")
    print("\nEvaluation terminee!")


if __name__ == "__main__":
    main()
