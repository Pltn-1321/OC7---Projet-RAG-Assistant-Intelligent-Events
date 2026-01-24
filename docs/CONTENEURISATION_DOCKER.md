# Conteneurisation avec Docker

## Table des matières

1. [Comment fonctionne Docker ?](#comment-fonctionne-docker)
2. [Pourquoi conteneuriser ?](#pourquoi-conteneuriser)
3. [Solution mise en place dans ce projet](#solution-mise-en-place-dans-ce-projet)

---

## Comment fonctionne Docker ?

### Le problème initial

Lors du déploiement d'une application, on rencontre souvent le problème classique :
*"Ça marche sur ma machine !"*. Les différences entre environnements (versions de Python,
dépendances système, configurations OS) causent des bugs imprévisibles.

### La solution : les conteneurs

Docker résout ce problème en empaquetant une application avec **tout son environnement
d'exécution** dans une unité standardisée appelée **conteneur**.

### Concepts clés

#### Image vs Conteneur

| Concept | Analogie | Description |
|---------|----------|-------------|
| **Image** | Une recette de cuisine | Un modèle immuable contenant le code, les dépendances et la configuration |
| **Conteneur** | Le plat préparé | Une instance en cours d'exécution créée à partir d'une image |

Une image peut générer plusieurs conteneurs identiques, tout comme une recette peut
produire plusieurs plats.

#### Dockerfile

Le `Dockerfile` est le fichier de configuration qui décrit comment construire une image.
Il contient une série d'instructions séquentielles :

```dockerfile
FROM python:3.11-slim    # Image de base
WORKDIR /app             # Répertoire de travail
COPY . .                 # Copier le code source
RUN pip install -r ...   # Installer les dépendances
CMD ["python", "app.py"] # Commande de démarrage
```

#### Couches (Layers)

Docker construit les images par **couches successives**. Chaque instruction du Dockerfile
crée une couche. Les couches sont mises en cache : si une couche n'a pas changé, Docker
la réutilise au lieu de la reconstruire.

```
┌─────────────────────────────────┐
│  CMD ["python", "app.py"]       │ ← Couche 5 (commande)
├─────────────────────────────────┤
│  COPY src/ ./src/               │ ← Couche 4 (code source) — change souvent
├─────────────────────────────────┤
│  RUN uv sync                    │ ← Couche 3 (dépendances) — change rarement
├─────────────────────────────────┤
│  COPY pyproject.toml .          │ ← Couche 2 (fichier de deps)
├─────────────────────────────────┤
│  FROM python:3.11-slim          │ ← Couche 1 (image de base) — stable
└─────────────────────────────────┘
```

**Optimisation** : on copie d'abord les fichiers de dépendances (`pyproject.toml`),
puis on installe les dépendances, et enfin on copie le code source. Ainsi, modifier
le code ne déclenche pas la réinstallation des dépendances.

#### Docker Compose

`docker-compose.yml` permet d'orchestrer **plusieurs conteneurs** (services) ensemble.
Il définit les ports, volumes, réseaux et dépendances entre services.

#### Volumes

Les volumes permettent de **persister les données** en dehors du conteneur. Sans volume,
les données sont perdues quand le conteneur est supprimé.

```
Hôte (machine locale)          Conteneur
┌──────────────────┐           ┌──────────────────┐
│  ./data/         │ ◄═══════► │  /app/data/      │
│  (persistant)    │  volume   │  (éphémère)      │
└──────────────────┘           └──────────────────┘
```

---

## Pourquoi conteneuriser ?

### 1. Reproductibilité

L'application fonctionne de manière **identique** sur toute machine disposant de Docker,
qu'il s'agisse du poste d'un développeur, d'un serveur de CI/CD ou d'un environnement
de production.

### 2. Isolation

Chaque conteneur est isolé du système hôte et des autres conteneurs. Les dépendances
d'un projet ne peuvent pas entrer en conflit avec celles d'un autre projet sur la
même machine.

### 3. Portabilité

Un conteneur Docker fonctionne sur Linux, macOS et Windows sans modification. Le
déploiement se résume à : *installer Docker + lancer le conteneur*.

### 4. Simplicité de déploiement

Au lieu d'un guide d'installation complexe (installer Python, uv, les dépendances,
configurer les variables d'environnement...), le déploiement se réduit à :

```bash
docker-compose up -d
```

### 5. Scalabilité

On peut lancer plusieurs instances du même conteneur derrière un load balancer pour
gérer plus de trafic, sans modifier le code.

### 6. Sécurité

Le conteneur limite la surface d'attaque en n'incluant que le strict nécessaire.
L'isolation empêche un processus compromis d'accéder au système hôte.

### Pertinence pour ce projet

Pour notre assistant RAG, la conteneurisation est particulièrement utile car :

- **Dépendances complexes** : FAISS, Mistral SDK, Streamlit, FastAPI — beaucoup de
  librairies avec des versions spécifiques à coordonner
- **Deux modes d'exécution** : API (FastAPI) et UI (Streamlit) — Docker permet de
  les isoler dans des services dédiés
- **Données persistantes** : L'index FAISS doit survivre aux redémarrages du conteneur
  grâce aux volumes
- **Variables sensibles** : Les clés API (Mistral, Open Agenda) sont injectées via
  l'environnement, jamais incluses dans l'image

---

## Solution mise en place dans ce projet

### Architecture Docker

Le projet utilise trois fichiers Docker :

| Fichier | Rôle |
|---------|------|
| `Dockerfile` | Définit comment construire l'image de l'application |
| `docker-compose.yml` | Orchestre les services API et Streamlit |
| `.dockerignore` | Exclut les fichiers inutiles du contexte de build |

### Le Dockerfile : build multi-stage

Notre Dockerfile utilise un **build multi-stage** (multi-étapes) pour optimiser la
taille de l'image finale. Cette technique permet de séparer l'installation des
dépendances de l'image de production.

#### Stage 1 : `base`

```dockerfile
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv
```

**Rôle** : Prépare l'image de base avec Python 3.11, `uv` et les outils système
minimaux (`curl` pour les healthchecks).

**Variables d'environnement** :
- `PYTHONDONTWRITEBYTECODE=1` : Évite la création de fichiers `.pyc` (inutiles dans
  un conteneur)
- `PYTHONUNBUFFERED=1` : Les logs Python s'affichent immédiatement (pas de buffer)
- `PIP_NO_CACHE_DIR=1` : Réduit la taille de l'image en désactivant le cache pip

#### Stage 2 : `dependencies`

```dockerfile
FROM base AS dependencies

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev --extra api
```

**Rôle** : Installe les dépendances Python dans un environnement virtuel. Les
dépendances de développement (`--no-dev`) et les notebooks sont exclues pour réduire
la taille.

**Optimisation du cache** : Seuls `pyproject.toml` et `uv.lock` sont copiés à cette
étape. Tant que ces fichiers ne changent pas, cette couche est réutilisée depuis le
cache Docker.

#### Stage 3 : `production`

```dockerfile
FROM base AS production

COPY --from=dependencies /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

COPY src/ src/
COPY app.py .
COPY scripts/ scripts/

RUN mkdir -p data/processed data/indexes data/raw

EXPOSE 8000 8501
```

**Rôle** : Assemble l'image finale en copiant uniquement l'environnement virtuel
(depuis le stage `dependencies`) et le code source. Le résultat est une image légère
sans les outils de build.

#### Entrypoint : mode API ou Streamlit

```dockerfile
COPY <<'EOF' /app/entrypoint.sh
#!/bin/bash
set -e

if [ "$1" = "streamlit" ]; then
    exec streamlit run app.py \
        --server.port=${STREAMLIT_PORT} \
        --server.address=0.0.0.0 \
        --server.headless=true
elif [ "$1" = "api" ] || [ -z "$1" ]; then
    exec uvicorn src.api.main:app \
        --host ${API_HOST} \
        --port ${API_PORT}
else
    exec "$@"
fi
EOF

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
```

Le script d'entrypoint permet de choisir le mode d'exécution :
- `docker run rag-events` → lance l'API FastAPI (mode par défaut)
- `docker run rag-events streamlit` → lance l'interface Streamlit
- `docker run rag-events <commande>` → exécute une commande arbitraire

#### Healthcheck

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${API_PORT}/health || exit 1
```

Docker vérifie toutes les 30 secondes que l'API répond sur `/health`. Après 3 échecs
consécutifs, le conteneur est marqué comme `unhealthy`, ce qui permet à Docker Compose
de redémarrer le service ou d'alerter un système de monitoring.

### Docker Compose : orchestration des services

Le fichier `docker-compose.yml` définit deux services qui fonctionnent ensemble :

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose                          │
│                                                             │
│  ┌─────────────────┐         ┌─────────────────────────┐   │
│  │   API FastAPI    │         │   Interface Streamlit   │   │
│  │   Port 8000     │◄────────│   Port 8501             │   │
│  │                  │ depends │                         │   │
│  │  healthcheck:    │   on    │  command: streamlit     │   │
│  │  /health         │         │                         │   │
│  └────────┬─────────┘         └────────────┬────────────┘   │
│           │                                │                │
│           └────────────┬───────────────────┘                │
│                        │                                    │
│              ┌─────────┴──────────┐                         │
│              │   rag-network      │                         │
│              │   (bridge)         │                         │
│              └─────────┬──────────┘                         │
│                        │                                    │
└────────────────────────┼────────────────────────────────────┘
                         │ volume
                ┌────────┴────────┐
                │   ./data/       │
                │   (host)        │
                └─────────────────┘
```

#### Service `api`

```yaml
api:
  build:
    context: .
    target: production
  ports:
    - "8000:8000"
  environment:
    - MISTRAL_API_KEY=${MISTRAL_API_KEY}
    - REBUILD_API_KEY=${REBUILD_API_KEY:-}
    - EMBEDDING_PROVIDER=${EMBEDDING_PROVIDER:-mistral}
    - LLM_MODEL=${LLM_MODEL:-mistral-small-latest}
  volumes:
    - ./data:/app/data
  restart: unless-stopped
```

Points importants :
- **`target: production`** : Utilise le stage `production` du build multi-stage
- **Variables d'environnement** : Lues depuis le fichier `.env` local avec des
  valeurs par défaut (`${VAR:-default}`)
- **Volume `./data`** : Monte le répertoire local `data/` dans le conteneur pour
  persister l'index FAISS
- **`restart: unless-stopped`** : Redémarrage automatique en cas de crash

#### Service `streamlit`

```yaml
streamlit:
  command: ["streamlit"]
  depends_on:
    api:
      condition: service_healthy
  ports:
    - "8501:8501"
```

Points importants :
- **`command: ["streamlit"]`** : Passe l'argument "streamlit" à l'entrypoint
- **`depends_on: service_healthy`** : Attend que l'API passe le healthcheck avant
  de démarrer — garantit que le backend est prêt

#### Réseau

```yaml
networks:
  rag-network:
    driver: bridge
```

Les deux services partagent un réseau Docker isolé (`bridge`). Ils peuvent communiquer
entre eux par leurs noms de service (ex: `http://api:8000`) sans exposer ces ports
à l'extérieur.

### Le `.dockerignore`

Le `.dockerignore` exclut les fichiers inutiles du contexte de build Docker. Cela
accélère le build et réduit la taille de l'image :

| Exclusion | Raison |
|-----------|--------|
| `.git/` | Historique Git inutile en production |
| `__pycache__/`, `*.pyc` | Fichiers compilés Python (régénérés) |
| `.venv/`, `venv/` | Environnement virtuel local (recréé dans le conteneur) |
| `data/*` | Données montées via volume |
| `tests/`, `notebooks/` | Inutiles en production |
| `docs/`, `*.md` | Documentation non nécessaire à l'exécution |
| `.env` | Secrets — **ne jamais inclure dans l'image** |

### Commandes de référence

#### Construction et lancement

```bash
# Construire l'image
docker build -t rag-events .

# Lancer l'API seule
docker run -p 8000:8000 --env-file .env -v $(pwd)/data:/app/data rag-events

# Lancer Streamlit seul
docker run -p 8501:8501 --env-file .env -v $(pwd)/data:/app/data rag-events streamlit

# Lancer les deux services avec Docker Compose
docker-compose up -d

# Lancer un service spécifique
docker-compose up api
docker-compose up streamlit
```

#### Monitoring et debug

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Vérifier l'état des conteneurs
docker-compose ps

# Entrer dans un conteneur en cours d'exécution
docker exec -it rag-events-api /bin/bash

# Vérifier le healthcheck
docker inspect --format='{{.State.Health.Status}}' rag-events-api
```

#### Arrêt et nettoyage

```bash
# Arrêter les services
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Supprimer les images non utilisées
docker image prune
```

### Flux de déploiement complet

```
1. Pré-requis
   └── Docker et Docker Compose installés
   └── Fichier .env avec MISTRAL_API_KEY

2. Préparation des données
   └── Exécuter les notebooks localement (01 à 04)
   └── OU monter un répertoire data/ existant

3. Construction
   └── docker-compose build
       ├── Stage base : Python 3.11 + uv
       ├── Stage dependencies : installation des packages
       └── Stage production : image finale optimisée

4. Lancement
   └── docker-compose up -d
       ├── API démarre (port 8000)
       ├── Healthcheck passe (/health → 200 OK)
       └── Streamlit démarre (port 8501)

5. Utilisation
   └── API : http://localhost:8000/docs (Swagger)
   └── UI  : http://localhost:8501
```

### Bonnes pratiques appliquées

| Pratique | Mise en oeuvre |
|----------|---------------|
| Build multi-stage | 3 stages (base, dependencies, production) |
| Image minimale | `python:3.11-slim` au lieu de l'image complète |
| Cache des couches | `pyproject.toml` copié avant le code source |
| Pas de secrets dans l'image | Variables d'environnement via `.env` |
| Healthchecks | Vérification périodique de `/health` |
| `.dockerignore` complet | Exclut tests, docs, notebooks, données |
| Redémarrage automatique | `restart: unless-stopped` |
| Réseau isolé | `rag-network` en mode bridge |
| Volumes pour les données | Index FAISS persisté sur l'hôte |
| Un processus par conteneur | API et Streamlit dans des conteneurs séparés |
