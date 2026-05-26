# Strates RI — Papier méthodologique

Ce dossier contient l'**article académique / working paper méthodologique**.

## Fichiers

- `main.tex` : **source unique** de l'article — document LaTeX complet hand-édité (préambule + corps + bibliographie natbib). C'est *la* vérité : le PDF et la page web en sont dérivés.
- `references_strates_ri.bib` : bibliographie BibTeX.
- `annexe_pilot_*.csv` : artefacts du pilote (scores par couche pour 1815–1848,
  1945–1962, 1991–2001 ; sensibilité par profil + `delta_max` + statut ; simulation de
  second codage). **Tous générés** par `scripts/generate_paper_artifacts.py` à partir
  des données canoniques/générées — aucun chiffre n'y est saisi à la main.
- `codebook_scoring_strates_ri.md` : codebook synthétique.
- `Dockerfile.tex` : image TeX Live dédiée à la compilation.

## Publication

- **Page web** : `scripts/generate_paper_mdx.py` génère `docs/PAPER.md` **depuis `main.tex`** (exécuté par `npm run generate:docs`, donc à chaque build). Publiée dans le site (sidebar « Papier (méthodologie) »).
- **PDF** : servi sur le site à `static/paper/strates_ri.pdf` (lien « Télécharger le PDF » sur la page).

### Recompiler le PDF (dans Docker, rien en local)

```bash
# 1. image TeX (une fois)
docker build -t ir-strata-tex -f paper/Dockerfile.tex .
# 2. compiler et publier le PDF directement depuis main.tex (la source)
docker run --rm -v "$PWD":/work -w /work/paper ir-strata-tex \
  latexmk -pdf -interaction=nonstopmode main.tex
cp paper/main.pdf static/paper/strates_ri.pdf
```

## Alignement sur l'application ir-strata

Cette version (4) est **alignée sur l'atlas ir-strata** : les scores du cas pilote 1945--1962, le nommage des familles (`marxism_dependency_structuralism`) et le traitement de l'anti-anachronisme reflètent exactement l'application. Anti-anachronisme **strict** : une théorie non émergée est *rejetée* (et non scorée faiblement) sur les couches doctrine et académique ; la synthèse ne porte alors que sur les familles présentes sur les trois couches.

## Limite méthodologique assumée

Le pilote couvre **trois périodes** (1815–1848, 1945–1962, 1991–2001) en **codage auteur unique**, complété d'une **simulation déterministe de second codage** explicitement marquée. Il démontre l'applicabilité, la robustesse aux pondérations et le contrôle de l'anachronisme du protocole, mais ne prouve pas la fiabilité inter-codeurs : la simulation ne remplace pas un codage humain indépendant. Verdict d'audit du papier : `partially_holds`. Le papier le dit explicitement et propose un protocole de validation indépendante.
