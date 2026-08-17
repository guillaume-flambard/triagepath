# WS1 — Frontend React (streaming agentic UX)

**Rôle Accenture cible :** "Implement agentic application UX: streaming responses,
intermediate output display, reasoning transparency, and error and escalation
interfaces for end users." C'est le signal n°1 du JD.

## Objectif

Un frontend **Next.js (App Router)** qui consomme l'API SSE existante
(`POST /api/analyze/stream` + `POST /api/review`) et rend la timeline live du
graphe LangGraph : les nodes s'allument en temps réel, la review humaine
s'affiche, le rapport final se construit. Local-first, offline-capable (mock).

## Contraintes / conventions

- Répertoire : `web/` à la racine du repo triagepath (Next.js App Router, TS).
- Design system sobre, aligné sur la marque : ink `#111418`, accent ocre
  `#C58A3C`, paper `#FAF9F6` (cohérent avec le logo 01 Path Fork).
- Pas de nouvelle dépendance backend : le front consomme les endpoints déjà
  testés. Le backend reste le seul à parler au graphe.
- Bilingue FR/EN avec toggle (hérité de la logique produit), locale par défaut
  `fr`.
- Modes LLM : `mock` (offline, par défaut), `ollama`, `groq`.

## Fonctionnalités (MVP)

1. **Écran de saisie** : preset (Lumea/SaaS), description libre, URL, ou manuel
   (nom + secteur + taille équipe + taux horaire + semaines/mois). Sélecteur de
   provider LLM.
2. **Timeline live (streaming)** : consomme `POST /api/analyze/stream` en SSE.
   - Chaque événement `node` ajoute une étape à la timeline avec son message.
   - `event: thread` affiche l'id de run.
   - `event: interrupt` affiche le panneau de review humaine.
   - `event: done` affiche le rapport final.
   - `event: error` affiche une bannière d'erreur avec relance.
3. **Review humaine (escalade)** : panneau avec Approve / Edit / Reject.
   - Approve → `POST /api/review {action:"approve"}` → stream rejoint le done.
   - Edit → formulaire (taux horaire, semaines/mois) → `action:"edit"`.
   - Reject → `action:"reject"`.
4. **Rapport final** : rendu du `final` (tâches scorées, priorité, deep-dives,
   rapport exécutif).
5. **Erreurs / retry** : bannière d'erreur + bouton relancer.

## Flux de données (contrat API)

```
POST /api/analyze/stream  body: AnalysisRequest  -> SSE
  event: thread    data: {thread_id}
  event: node      data: {node, message}
  event: interrupt data: {payload}
  event: done      data: {final, thread_id}
  event: error     data: {message}

POST /api/review    body: {thread_id, action, hourly_rate?, weeks_per_month?, tasks?}
  -> {thread_id, final, events}
```

## Structure cible

```
web/
  app/
    page.tsx          # écran de saisie
    run/[threadId]/page.tsx   # timeline + review + rapport
  components/
    AnalysisForm.tsx
    Timeline.tsx
    NodeStep.tsx
    ReviewPanel.tsx
    FinalReport.tsx
    ErrorBanner.tsx
  lib/
    sse.ts            # helper fetch + parse SSE
    api.ts            # analyse/review clients
  package.json / tsconfig / next.config
```

## Definition of done (MVP WS1)

- [ ] `web/` démarre (`npm run dev`), parle au backend (`/api` proxied).
- [ ] Saisie preset Lumea → timeline stream les nodes ingest→score→deep_dive.
- [ ] Interrupt review s'affiche ; Approve → rapport final rendu.
- [ ] Mode mock fonctionne offline, sans clé.
- [ ] Bilingue FR/EN, design sobre cohérent avec la marque.
- [ ] `npm run build` passe (TS strict).
