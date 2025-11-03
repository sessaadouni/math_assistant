# Math RAG Frontend - Architecture modulaire

## 📁 Structure du projet

```
client/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── layout.tsx         # Layout principal avec Providers
│   │   ├── page.tsx           # Page d'accueil
│   │   ├── MathRagApp.tsx     # Composant principal
│   │   └── globals.css        # Styles globaux
│   │
│   ├── components/
│   │   ├── Providers.tsx      # TanStack Query Provider
│   │   │
│   │   ├── ui/                # Composants UI réutilisables
│   │   │   ├── Button.tsx     # Bouton avec variants et loading
│   │   │   ├── Input.tsx      # Champ de saisie avec label/error
│   │   │   ├── TextArea.tsx   # Zone de texte
│   │   │   ├── Select.tsx     # Liste déroulante
│   │   │   ├── Card.tsx       # Carte avec glass morphism
│   │   │   ├── MarkdownMath.tsx  # Rendu Markdown + KaTeX
│   │   │   ├── OutputBox.tsx  # Container avec loading/error
│   │   │   └── index.ts       # Barrel export
│   │   │
│   │   └── features/          # Composants métier
│   │       ├── Header.tsx     # En-tête avec status backend
│   │       ├── PanelSelector.tsx  # Navigation par onglets
│   │       ├── ChatPanel.tsx  # Panel Q&A
│   │       ├── SheetPanel.tsx # Panel génération fiches
│   │       ├── ReviewPanel.tsx    # Panel correction
│   │       ├── FormulaPanel.tsx   # Panel formules
│   │       ├── ExamPanel.tsx  # Panel examens
│   │       ├── CoursePanel.tsx    # Panel résumés
│   │       ├── GradePanel.tsx # Panel notation
│   │       └── index.ts       # Barrel export
│   │
│   ├── hooks/                 # Custom React hooks
│   │   ├── useStream.ts       # Hook pour streaming SSE
│   │   ├── useBackendHealth.ts    # Hook status backend
│   │   ├── useLocalStorage.ts # Hook persistance
│   │   └── index.ts           # Barrel export
│   │
│   ├── lib/                   # Utilitaires et logique
│   │   ├── api.ts            # Client API backend
│   │   ├── sse.ts            # Logique streaming SSE
│   │   ├── markdown.ts       # Enhancement markdown
│   │   └── utils.ts          # Fonctions utilitaires
│   │
│   ├── types/                 # Types TypeScript
│   │   └── index.ts          # Toutes les interfaces
│   │
│   └── styles/
│       └── math-rag.css      # Styles markdown + math
│
├── tsconfig.json             # Config TypeScript avec @/ alias
└── package.json
```

## 🎯 Principes d'architecture

### 1. **Séparation des responsabilités**
- **UI Components** : Composants réutilisables, pas de logique métier
- **Feature Components** : Composants métier, contiennent la logique
- **Hooks** : Logique réutilisable (API calls, state management)
- **Lib** : Utilitaires purs, sans dépendances React

### 2. **Imports avec alias @/**
```typescript
import { Button, Card } from '@/components/ui';
import { useStream } from '@/hooks';
import { MathRagAPI } from '@/lib/api';
import type { PanelType } from '@/types';
```

### 3. **TanStack Query**
- Gestion des appels API et cache
- `useStream` : Mutation pour streaming SSE
- `useBackendHealth` : Query pour status backend

### 4. **Persistance locale**
- `useLocalStorage` hook pour sauvegarder les formulaires
- Restore automatique au chargement

## 🚀 Utilisation

### Composants UI

```tsx
import { Button, Input, Card } from '@/components/ui';

<Card title="Mon titre" variant="gradient">
  <Input label="Email" icon="📧" />
  <Button isLoading={true} icon="🚀">
    Envoyer
  </Button>
</Card>
```

### Hooks

```tsx
import { useStream, useBackendHealth } from '@/hooks';

const streamMutation = useStream();
const { data: health, isLoading } = useBackendHealth();

streamMutation.mutate({
  url: 'http://localhost:8000/chat?question=test',
  onToken: (token) => console.log(token),
  onError: (err) => console.error(err)
});
```

### API Client

```tsx
import { MathRagAPI } from '@/lib/api';

const api = new MathRagAPI('http://localhost:8000');
const url = api.buildChatUrl('Ma question', 5, 'cours', 'Chapitre 1');
```

## 📦 Dépendances principales

- **Next.js 15** - Framework React
- **TanStack Query** - Data fetching et cache
- **Framer Motion** - Animations
- **React Markdown** - Rendu markdown
- **KaTeX** - Rendu formules mathématiques
- **Tailwind CSS** - Styling

## 🔧 Configuration

### TypeScript paths (tsconfig.json)
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### TanStack Query Provider
Wrappé dans `layout.tsx` via `<Providers>`

## 🎨 Styling

- **Tailwind** : Classes utilitaires
- **Glass morphism** : `backdrop-blur-md bg-white/10`
- **Gradients** : `from-blue-600 to-purple-600`
- **Custom CSS** : `styles/math-rag.css` pour markdown/math

## 🐛 Debug

Tous les panels ont des logs console :
- 🚀 Début d'action
- 📡 URL construite
- 📥 Token reçu
- ✅ Succès
- ❌ Erreur

## 📝 Notes

- L'ancien composant monolithique reste dans `components/MathRagApp.tsx`
- La nouvelle version modulaire est dans `src/app/MathRagApp.tsx`
- Les deux versions coexistent pour migration progressive
