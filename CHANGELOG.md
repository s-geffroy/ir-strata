# Changelog

## [Unreleased] — ir-strata

### Changed

- Projet renommé **ir-strata** (fork du scaffold `ir-theory-historical-weighting-atlas-v1`).
- `docusaurus.config.ts` : `projectName` par défaut → `ir-strata` (url/baseUrl dérivés).

### Added

- Couche Docker : `Dockerfile` (Node 20 + Python 3 + ca-certificates), `docker-compose.yml` (services `dev` et `preview`), `.dockerignore`. Exécution 100 % conteneurisée, rien installé en local.
- `docs/DATA_PROVENANCE.md` : statut explicite des données = seed généré non vérifié, à re-sourcer.
- **Audit de provenance des références** : `scripts/audit_references.py` (Crossref + OpenLibrary, stdlib seule, hors pipeline de build). Rapport machine `references/audit_report.json` et rapport publié `docs/AUDIT_REFERENCES.md`. Résultat initial : **56/56 références vérifiées, 0 hallucination**.
- **Découplage de la synthèse** : `compute_scores.py` génère `annual_interpolated_layers.json` (séries temporelles par couche) et `scores_synthesis_sensitivity.json` (plage min/max de la synthèse sous les 5 profils de pondération = incertitude d'agrégation).
- Frontend : composants `TheoryAreaChart` (graphe par couche paramétrable) et `HistoricalLayersView` (vue par défaut = 3 couches séparées, synthèse reléguée derrière un avertissement). `PeriodScoreTable` refondu en colonnes par couche + plage de synthèse. Accueil et Explorer mis à jour. Doc `methodology/AGGREGATION.md` complétée.
- **Anti-anachronisme automatisé** : nouvelle donnée canonique `theory_emergence.json` (années d'émergence par famille × couche, justifiées) ; `scripts/audit_anachronism.py` (détection + rejet `--write`, rapport publié `docs/AUDIT_ANACHRONISM.md`) ; garde au build dans `validate_model.py` (échec sur anachronisme non rejeté/non justifié). **446 scores anachroniques détectés et rejetés** (`deprecated`) : la couche `academic_influence` ne se peuple qu'à partir de l'émergence des écoles (~1890-1919+), conformément à la règle §9. Doc `methodology/ANTI_ANACHRONISM.md` complétée.
- **Normalisation repensée (non-exclusivité)** : bascule **Brut / Normalisé** dans `HistoricalLayersView` ; le mode brut affiche des lignes **non empilées** (intensités indépendantes 0-100). Avertissement de non-exclusivité/non-exhaustivité des familles en vue normalisée. `PeriodScoreTable` affiche désormais brut + part normalisée par cellule. Docs `methodology/SCORING.md` et page d'accueil complétées.
- **Politique de maturité (honnêteté du statut)** : `scripts/enforce_maturity_policy.py` réserve `reviewed`/`validated` aux périodes P1 ; garde au build dans `validate_model.py`. **21 objets hors P1 rétrogradés en `draft`** (16 preuves, 5 événements). Références exemptées (validées par l'audit). Doc `DATA_PROVENANCE.md` complétée.
- **Pipeline & CI** : modes `--check` (read-only) sur les trois audits ; scripts npm `check:data` (gardes hors ligne), `audit:refs` (réseau), `data:refresh` (passes mutantes à la demande). Workflow GitHub Actions complété (check:data + audit:refs avant build). Doc `implementation/BUILD_PIPELINE.md` réécrite (deux pistes : build déterministe / rafraîchissement).
- **Re-sourçage des scores** : champ `calibration_status` (`seed`/`sourced`) ; rapport d'avancement `scripts/calibration_report.py` → `docs/CALIBRATION_STATUS.md`. **Les 1549 scores actifs (globaux + entités, 14 périodes) ont été re-sourcés (100 %)** : justifications analytiques réelles, références vérifiées, anti-anachronisme appliqué couche par couche.
- **Recalibrage des profils d'entités dupliqués** : différenciation des valeurs `raw_score` des entités à profil seed identique au sein d'une même période (Chine vs URSS/USA/Russie, OTAN vs USA, UE vs institutions, etc.) sur les 9 périodes concernées. **0 cluster de profil dupliqué restant** dans l'atlas. `known_limits` mis à jour.
- **CI** : bump des actions GitHub vers les versions sur Node.js 24 (`checkout@v6`, `setup-node@v6`, `setup-python@v6`, `configure-pages@v6`, `upload-pages-artifact@v5`, `deploy-pages@v5`), pour anticiper la dépréciation de Node 20 (2 juin 2026).
- **Cohérence des niveaux de confiance** : `anachronism_risk` des scores `strategic_reality` recalculé en fonction de l'écart à la disponibilité des idées (`political_doctrine_from`) — un usage rétrospectif d'une lentille moderne (constructivisme en 1815, etc.) porte désormais un risque élevé, les lentilles anciennes (réalisme, géopolitique) restant à risque bas. Cascade sur `internal_score` et `label` (formule officielle). 248 scores corrigés ; rétrospectif moyen 30 → 45.
- **Cohérence `anachronism_risk` des scores rejetés** : les 445 scores rejetés pour anachronisme (`deprecated`, bloc `anachronism`) portaient un risque bas (~30) malgré leur statut. Recalcul d'un risque élevé (65–100, calé sur l'écart à l'émergence) + cascade `internal_score`/`label`. `anachronism_risk` est désormais cohérent sur toutes les couches et statuts (rejetés ~77, actifs doctrine/académique ~29).

### Notes

- Les données canoniques fournies sont marquées comme **seed non vérifié** (`source_status: draft_unverified_seed`) : elles servent à faire tourner la chaîne, pas de valeur historique de référence. Vérification/re-sourçage prévus en phase ultérieure.

## v1.0.0-atlas-v1

### Added

- Première architecture Docusaurus optimisée GitHub Pages.
- Données canoniques JSON.
- Scores globaux seed pour 1815-2026.
- Entités P1 seed avec pondérations systémiques.
- Événements-pivots, preuves, controverses et bibliographie V1.
- Scripts de validation et génération.
- Workflow GitHub Actions Pages.
