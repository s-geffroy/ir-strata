# ir-strata — Pondération historique des théories des relations internationales (Atlas V1)

Atlas analytique statique prêt pour GitHub Pages, construit avec Docusaurus.

> **Statut des données :** le jeu de scores/preuves/références fourni est un **seed généré, non vérifié**, à re-sourcer (voir `docs/DATA_PROVENANCE.md`). Il sert à faire tourner la chaîne technique, pas d'autorité historique.

## Ce que contient le pack

- Modèle méthodologique complet : taxonomie, scoring, confiance, anti-anachronisme, agrégation.
- Données canoniques JSON : scores bruts, périodes, théories, entités, preuves, événements, controverses, références.
- Données générées : scores normalisés, synthèse, valeurs annuelles, CSV.
- Site Docusaurus optimisé GitHub Pages.
- Workflow GitHub Actions pour validation, build et déploiement.
- Prompt d’implémentation complet pour LLM/agent de code.

## Démarrage (Docker uniquement)

Tout tourne dans un container ; rien n'est installé en local.

```bash
# Dev avec hot-reload (pipeline Python + Docusaurus) → http://localhost:3000/ir-strata/
docker compose up dev

# Aperçu du build statique de production → http://localhost:3001/ir-strata/
docker compose --profile preview up preview
```

L'image embarque Node 20 + Python 3 ; les scripts du pipeline n'utilisent que la stdlib.

## Build GitHub Pages

Le build de production est produit par le service `preview` (`npm run build`),
dossier statique `build/`.

## Configuration GitHub Pages

Dans le dépôt GitHub :

1. `Settings` → `Pages`.
2. `Build and deployment` → `Source` = `GitHub Actions`.
3. Modifier `docusaurus.config.ts` si nécessaire :
   - `organizationName`
   - `projectName`
   - `url`
   - `baseUrl`

## Règle canonique

```text
src/data/canonical/*.json = source analytique
src/data/generated/*.json = dérivés calculés
static/exports/* = exports publics
```

Les scores normalisés ne doivent jamais être édités à la main.

## Statut

`Atlas V1 · Révisable · Méthodologie documentée`

Les données seed sont structurées et exploitables, mais plusieurs objets restent marqués `draft` ou `reviewed`. La publication ne doit pas être vendue comme mesure objective directe.
