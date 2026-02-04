# Frontend - RAG Events Assistant

> Interface utilisateur React pour l'assistant conversationnel d'événements culturels

[![React 18](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5+-646CFF.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3+-38B2AC.svg)](https://tailwindcss.com/)

---

## Présentation

Interface chat moderne pour interagir avec l'assistant RAG. Permet de poser des questions en langage naturel pour découvrir des événements culturels.

### Fonctionnalités

- Chat conversationnel en temps réel
- Affichage des événements recommandés avec détails
- Historique de conversation
- Thème sombre moderne
- Design responsive

---

## Stack Technique

| Technologie | Version | Rôle |
|-------------|---------|------|
| React | 18+ | Framework UI |
| TypeScript | 5+ | Typage statique |
| Vite | 5+ | Build tool & dev server |
| Tailwind CSS | 3+ | Styling utility-first |
| shadcn/ui | - | Composants UI |
| Lucide React | - | Icônes |

---

## Installation

### Prérequis

- Node.js 18+ ([Download](https://nodejs.org/))
- npm ou pnpm

### Setup

```bash
# Installer les dépendances
npm install

# Copier la configuration
cp .env.example .env.local

# Éditer .env.local et configurer l'URL de l'API
# VITE_API_URL=http://localhost:8000
```

---

## Développement

```bash
# Lancer le serveur de développement
npm run dev
# → http://localhost:5173

# Build de production
npm run build

# Preview du build
npm run preview

# Linting
npm run lint

# Type checking
npx tsc --noEmit
```

---

## Structure du Projet

```
frontend/
├── src/
│   ├── components/       # Composants React
│   │   ├── ui/           # Composants shadcn/ui
│   │   └── chat/         # Composants spécifiques au chat
│   ├── hooks/            # Custom hooks
│   ├── lib/              # Utilitaires
│   ├── services/         # Services API
│   ├── types/            # Types TypeScript
│   ├── App.tsx           # Composant racine
│   ├── main.tsx          # Point d'entrée
│   └── index.css         # Styles globaux (Tailwind)
├── public/               # Assets statiques
├── docs/                 # Documentation frontend
├── index.html            # Template HTML
├── package.json          # Dépendances
├── tailwind.config.js    # Configuration Tailwind
├── tsconfig.json         # Configuration TypeScript
└── vite.config.ts        # Configuration Vite
```

---

## Configuration

### Variables d'environnement

| Variable | Description | Défaut |
|----------|-------------|--------|
| `VITE_API_URL` | URL de l'API backend | `http://localhost:8000` |

### Fichiers de configuration

- **vite.config.ts** - Configuration Vite (proxy, plugins)
- **tailwind.config.js** - Thème et extensions Tailwind
- **tsconfig.json** - Options TypeScript
- **components.json** - Configuration shadcn/ui

---

## API Integration

Le frontend communique avec le backend via REST API :

```typescript
// services/api.ts
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Endpoints utilisés
POST /chat      // Envoi de message avec session
GET  /health    // Health check
```

---

## Docker

```bash
# Build l'image
docker build -t rag-events-frontend .

# Run en développement
docker build --target development -t rag-events-frontend-dev .
docker run -p 5173:5173 -v $(pwd)/src:/app/src rag-events-frontend-dev

# Run en production
docker run -p 5173:5173 rag-events-frontend
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [CHAT_IMPLEMENTATION.md](docs/CHAT_IMPLEMENTATION.md) | Détails de l'implémentation du chat |

---

## Contribution

1. Respecter les conventions ESLint/Prettier
2. Typer correctement avec TypeScript
3. Utiliser les composants shadcn/ui existants
4. Tester les composants avant de soumettre

---

## Retour au projet principal

Voir [../README.md](../README.md) pour la documentation complète du monorepo.
