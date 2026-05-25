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
- **Cohérence preuves ↔ théories** : vérification de l'intégrité référentielle du graphe (scores ↔ preuves ↔ références ↔ entités/événements/controverses) — aucune référence cassée ni période incohérente. Complété `related_theories` de 5 preuves structurelles majeures (bipolarité, décolonisation, dépendance, rivalité sino-américaine…) avec les théories des scores **actifs** qui les citent. Mismatches sur scores actifs : 0 (les liens des scores rejetés anachroniques restent volontairement non endossés).
- **Cohérence des controverses** : intégrité du graphe vérifiée (scores liés existants, dans les bonnes périodes, non rejetés ; théories des positions = théories des scores liés ; décision présente partout). Traduction des 6 `label_en` qui étaient des copies du français (site bilingue).
- **Positions des controverses étoffées** : les 18 `summary_fr` génériques (« Lecture privilégiant X. ») remplacés par des résumés réels et spécifiques de chaque lecture (réaliste, marxiste, constructiviste…), ancrés sur les références citées ; ajout des `summary_en` (site bilingue).
- **Papier académique (« Chemin A ») importé et aligné** : `paper/` (article, bibliographie BibTeX, codebook, CSV pilote). Réconcilié sur l'application : scores pilotes 1945-1962, nommage `marxism_dependency_structuralism`, et anti-anachronisme **strict** (rejet plutôt que score faible ; synthèse limitée aux familles présentes sur les 3 couches). Tableaux, exemples détaillés, analyse de sensibilité et codebook mis à jour.
- **Publication du papier** : page web `docs/PAPER.md` générée depuis le `.txt` source (`scripts/generate_paper_mdx.py`, intégré à `generate:docs`), au sidebar « Papier (méthodologie) ». **PDF** compilé via une image TeX Live dédiée (`paper/Dockerfile.tex` + `scripts/generate_paper_tex.py` → `paper/main.tex` → `static/paper/strates_ri_chemin_a.pdf`), lien de téléchargement sur la page (via `useBaseUrl`).
- **CI : audit des références non bloquant** : l'étape `audit:refs` de `deploy-pages.yml` passe en `continue-on-error: true`. Elle interroge des API tierces (Crossref, OpenLibrary) qui peuvent être indisponibles ou rate-limitées — OpenLibrary renvoie actuellement `HTTP 403`, ce qui faisait échouer le déploiement sur 5 références pourtant réelles et correctes (Said 1978, Spivak 1988, Kissinger 1994, Westad 2005, Acharya 2014). Une panne d'API externe ne doit pas bloquer la publication ; l'audit continue de tourner et de publier son rapport.
- **Pilote étendu à trois périodes (papier)** : le cas pilote auteur unique 1945–1962 est étendu à **1815–1848** et **1991–2001**, en *dérivant* tous les chiffres des données canoniques de l'application (aucun recodage parallèle). Nouvelles sections du papier : extension du pilote (avec le résultat fort « 1815–1848 n'a aucune synthèse » — couche académique inexistante avant ~1890), sensibilité comparée aux pondérations sur les périodes synthétisables, **simulation déterministe de second codage** (explicitement marquée comme ne valant pas une fiabilité inter-codeurs ; MAD 3.55, écart max 8, 0 score `contested`), et **audit de cohérence méthodologique** répondant aux cinq questions (trivialité, absurdité, sensibilité, chevauchement, anachronisme) avec **verdict explicite `partially_holds`**, raisons et conditions d'amélioration. Abstract et Annexe C mis à jour ; nouvelle Annexe D (artefacts). Nouveaux CSV annexes dérivés : `annexe_pilot_scores_1815_1848.csv`, `annexe_pilot_scores_1991_2001.csv`, `annexe_pilot_sensitivity.csv`, `annexe_pilot_intercoder_simulation.csv`.
- **PDF du papier en CI** : le workflow génère `paper/main.tex` puis compile le PDF (`xu-cheng/latex-action@v4`, TeX Live complet) et le publie dans `static/paper/` avant le build — le PDF servi reste toujours synchronisé avec la source du papier.

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
