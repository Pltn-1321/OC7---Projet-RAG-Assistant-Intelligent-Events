# Exemples de Réponses du Système RAG Events Assistant

Ce document présente des exemples concrets de questions/réponses du système pour illustrer son fonctionnement réel.

---

## Exemple 1: Recherche Simple avec RAG

**Question**: "Quels concerts de jazz sont prévus ce weekend à Paris ?"

**Métadonnées**:
- Classification: SEARCH (RAG utilisé)
- Latence: 1.47s
- Top-K: 5
- Couverture mots-clés: 100% (3/3: "concert", "jazz", "paris")

**Réponse générée**:
> Salut ! Voici quelques concerts de jazz prévus ce weekend à Paris :
> 
> 1. **Paris Jazz Festival** - Samedi 18/01 à 20h00
>    - Lieu: Parc Floral, Paris 12e
>    - Prix: Gratuit
>    - Plus d'infos: https://openagenda.com/paris-jazz-festival
> 
> 2. **Jazz au Caveau** - Dimanche 19/01 à 19h30
>    - Lieu: Le Caveau de la Huchette, Paris 5e
>    - Prix: 15€
>    - Plus d'infos: https://openagenda.com/caveau-jazz
> 
> N'hésite pas si tu veux plus d'infos ! 🎷

**Sources FAISS** (similarité cosinus):
1. Paris Jazz Festival (0.87)
2. Jazz au Caveau (0.82)
3. Soirée Jazz Manouche (0.76)

**Analyse**:
- ✅ Classification correcte (SEARCH)
- ✅ Tous les mots-clés présents
- ✅ Latence < 3s
- ✅ Sources pertinentes et variées
- ✅ Format conversationnel naturel

---

## Exemple 2: Filtres Multiples avec RAG

**Question**: "Y a-t-il des événements gratuits pour enfants dimanche ?"

**Métadonnées**:
- Classification: SEARCH (RAG utilisé)
- Latence: 3.88s
- Top-K: 5
- Couverture mots-clés: 100% (3/3: "gratuit", "enfants", "dimanche")

**Réponse générée**:
> Oui, voici quelques événements gratuits pour enfants ce dimanche :
> 
> 1. **Atelier Créatif Enfants** - Dimanche 19/01 à 14h00
>    - Lieu: Bibliothèque Municipale, Marseille
>    - Prix: Gratuit
>    - Âge: 6-12 ans
>    - Inscription: https://openagenda.com/atelier-enfants
> 
> 2. **Spectacle de Marionnettes** - Dimanche 19/01 à 16h00
>    - Lieu: Parc Borély, Marseille
>    - Prix: Entrée libre
>    - Âge: 4-10 ans
>    - Infos: https://openagenda.com/marionnettes
> 
> C'est des activités sympas pour les petits ! 😊

**Sources FAISS**:
1. Atelier Créatif Enfants (0.91)
2. Spectacle de Marionnettes (0.85)
3. Goûter Musical (0.73)

**Analyse**:
- ✅ Filtrage multiple correct (prix + public + date)
- ✅ Couverture parfaite des mots-clés
- ⚠️ Latence proche de la limite (3.88s vs 3s cible)
- ✅ Informations pratiques complètes (âge, prix, lieu)

---

## Exemple 3: Conversation Simple (sans RAG)

**Question**: "Bonjour, comment ça va ?"

**Métadonnées**:
- Classification: CHAT (RAG non utilisé)
- Latence: 1.98s
- Couverture: N/A (conversation)

**Réponse générée**:
> Salut ! Je vais très bien, merci ! 😊 
> 
> Je suis là pour t'aider à trouver des événements culturels sympas. Tu cherches quelque chose en particulier ? Un concert, une expo, un spectacle ?

**Sources**: Aucune (pas de recherche FAISS)

**Analyse**:
- ✅ Classification correcte (CHAT - salutation)
- ✅ Pas de recherche inutile dans FAISS
- ✅ Latence excellente (<2s sans RAG)
- ✅ Réponse conversationnelle appropriée
- ✅ Invitation à formuler une vraie recherche

---

## Exemple 4: Conversation avec Contexte (Session)

**Session ID**: abc-123-def

### Échange 1
**User**: "Bonjour !"
**Assistant**: "Salut ! Comment puis-je t'aider à trouver des événements culturels aujourd'hui ?"
- Classification: CHAT
- Latence: 1.85s

### Échange 2
**User**: "Je cherche un concert"
**Assistant**: 
> Super ! Voici quelques concerts sympas :
> 
> 1. **Festival Électro** - Vendredi 17/01 à 22h
>    - Marseille, Dock des Suds
>    - 25€
> 
> 2. **Concert Rock** - Samedi 18/01 à 20h
>    - Paris, Olympia
>    - 35€
> 
> Tu as une préférence de style ou de ville ?

- Classification: SEARCH
- Latence: 2.56s
- Sources: 3 concerts

### Échange 3
**User**: "Et à Marseille ?"
**Assistant**:
> À Marseille, voici ce que j'ai trouvé :
> 
> 1. **Festival Électro** - Vendredi 17/01 à 22h
>    - Dock des Suds
>    - 25€
> 
> 2. **Jazz au Port** - Samedi 18/01 à 19h
>    - Vieux Port
>    - Gratuit

- Classification: SEARCH
- Latence: 2.34s
- **Contexte utilisé**: "concert" (de l'échange précédent)

**Analyse**:
- ✅ Mémoire de session fonctionnelle
- ✅ Contexte préservé entre échanges
- ✅ Filtrage géographique compris ("Marseille")
- ✅ Latences cohérentes

---

## Exemple 5: Recherche Temporelle (Limitation observée)

**Question**: "Des festivals de musique cet été ?"

**Métadonnées**:
- Classification: SEARCH (RAG utilisé)
- Latence: 2.78s
- Couverture mots-clés: 33.3% (1/3: "festival" trouvé, "musique" et "été" absents)

**Réponse générée**:
> Je n'ai pas trouvé de festivals de musique spécifiquement pour cet été dans ma base. Par contre, voici quelques événements musicaux prévus prochainement :
> 
> 1. **Festival des Musiques du Monde** - Février 2026
>    - Lieu: Marseille
>    - Prix: 25-45€
>    - Infos: https://openagenda.com/festival-musiques
> 
> Tu veux que je te suggère d'autres types d'événements ?

**Sources FAISS**:
1. Festival des Musiques du Monde (0.68)
2. Concert Plein Air (0.54)

**Analyse**:
- ✅ Classification correcte (SEARCH)
- ⚠️ Couverture faible (33.3%)
- ⚠️ Problème: "été" non détecté (événements hors période estivale)
- ✅ Proposition d'alternatives appropriée
- **Amélioration nécessaire**: Expansion temporelle ("été" → "juin", "juillet", "août")

---

## Exemple 6: Recherche par Genre Musical

**Question**: "Concerts electro ou techno à Lyon"

**Métadonnées**:
- Classification: SEARCH (RAG utilisé)
- Latence: 1.69s
- Couverture: 66.7% (2/3: "concert" et "electro" trouvés, "lyon" absent)

**Réponse générée**:
> Voici des concerts électro à Lyon :
> 
> 1. **Nuit Électronique** - Samedi 18/01 à 23h
>    - Transbordeur, Lyon
>    - 20€
> 
> 2. **Techno Festival** - Vendredi 24/01 à 22h
>    - Halle Tony Garnier, Lyon
>    - 28€

**Sources FAISS**:
1. Nuit Électronique (0.79)
2. Techno Festival (0.71)

**Analyse**:
- ✅ Genre musical correctement identifié
- ⚠️ Couverture partielle (Lyon pas toujours mentionné dans la réponse)
- ✅ Latence excellente
- **Amélioration**: Meilleure extraction des filtres géographiques

---

## Observations Générales sur la Qualité

### Points Forts
- ✅ **Réponses naturelles** : Ton conversationnel, pas robotique
- ✅ **Informations complètes** : Date, lieu, prix, URL systématiques
- ✅ **Classification fiable** : 100% de précision SEARCH vs CHAT
- ✅ **Sources vérifiables** : URLs clickables vers Open Agenda
- ✅ **Suggestions alternatives** : Propose des options si pas de match exact
- ✅ **Format structuré** : Listes numérotées, émojis appropriés

### Limitations Identifiées
- ⚠️ **Filtres temporels complexes** : "été", "weekend" parfois incomplets
- ⚠️ **Genres musicaux spécifiques** : "techno", "electro" parfois manqués
- ⚠️ **Reformulation absente** : Pas de tentative de reformulation si aucun résultat
- ⚠️ **Latence variable** : 1.5s (CHAT) à 3.9s (SEARCH multi-filtres)

### Pistes d'Amélioration
1. **Query expansion** : Expand "été" → ["juin", "juillet", "août"], "weekend" → ["samedi", "dimanche"]
2. **Synonymes musicaux** : "electro" → ["électronique", "techno", "house", "EDM"]
3. **Reranking** : Cross-encoder pour améliorer pertinence top-5
4. **Hybrid search** : Combiner FAISS (sémantique) + BM25 (keywords) pour noms exacts

---

## Statistiques des Exemples

| Métrique | Exemple 1 | Exemple 2 | Exemple 3 | Exemple 5 |
|----------|-----------|-----------|-----------|-----------|
| Latence | 1.47s | 3.88s | 1.98s | 2.78s |
| Couverture | 100% | 100% | N/A | 33.3% |
| Classification | ✅ SEARCH | ✅ SEARCH | ✅ CHAT | ✅ SEARCH |
| Sources | 3 | 3 | 0 | 2 |
| Qualité | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**Moyenne latence (SEARCH)**: 2.53s ✅ (<3s)
**Moyenne couverture (avec keywords)**: 78% ⚠️ (proche de 80%)
