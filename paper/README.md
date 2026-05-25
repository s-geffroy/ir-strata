# Strates RI — Papier Chemin A

Ce dossier contient une version réorientée vers le **chemin A : article académique / working paper sérieux**.

## Fichiers

- `papier_strates_ri_chemin_a.txt` : **source unique** de l'article (LaTeX inline avec `\citep`).
- `references_strates_ri_chemin_a.bib` : bibliographie BibTeX.
- `annexe_pilot_scores_1945_1962.csv` : scores pilotes 1945–1962 (alignés sur l'atlas).
- `annexe_pilot_scores_1815_1848.csv` : scores pilotes 1815–1848 (aucune synthèse : couche académique inexistante avant ~1890).
- `annexe_pilot_scores_1991_2001.csv` : scores pilotes 1991–2001 (sept familles synthétisables).
- `annexe_pilot_sensitivity.csv` : synthèse par profil de pondération + `delta_max` + statut.
- `annexe_pilot_intercoder_simulation.csv` : codage principal vs second codage simulé (écarts).
- `codebook_scoring_strates_ri.md` : codebook synthétique.
- `main.tex` : wrapper LaTeX compilable, **généré** par `scripts/generate_paper_tex.py`.
- `Dockerfile.tex` : image TeX Live dédiée à la compilation.

## Publication

- **Page web** : `scripts/generate_paper_mdx.py` génère `docs/PAPER.md` (exécuté par `npm run generate:docs`, donc à chaque build). Publiée dans le site (sidebar « Papier (méthodologie) »).
- **PDF** : servi sur le site à `static/paper/strates_ri_chemin_a.pdf` (lien « Télécharger le PDF » sur la page).

### Recompiler le PDF (dans Docker, rien en local)

```bash
# 1. image TeX (une fois)
docker build -t ir-strata-tex -f paper/Dockerfile.tex .
# 2. (re)générer le wrapper depuis le .txt
docker compose run --rm dev python3 scripts/generate_paper_tex.py
# 3. compiler et publier le PDF
docker run --rm -v "$PWD":/work -w /work/paper ir-strata-tex \
  latexmk -pdf -interaction=nonstopmode main.tex
cp paper/main.pdf static/paper/strates_ri_chemin_a.pdf
```

## Alignement sur l'application ir-strata

Cette version (4) est **alignée sur l'atlas ir-strata** : les scores du cas pilote 1945--1962, le nommage des familles (`marxism_dependency_structuralism`) et le traitement de l'anti-anachronisme reflètent exactement l'application. Anti-anachronisme **strict** : une théorie non émergée est *rejetée* (et non scorée faiblement) sur les couches doctrine et académique ; la synthèse ne porte alors que sur les familles présentes sur les trois couches.

## Limite méthodologique assumée

Le pilote couvre **trois périodes** (1815–1848, 1945–1962, 1991–2001) en **codage auteur unique**, complété d'une **simulation déterministe de second codage** explicitement marquée. Il démontre l'applicabilité, la robustesse aux pondérations et le contrôle de l'anachronisme du protocole, mais ne prouve pas la fiabilité inter-codeurs : la simulation ne remplace pas un codage humain indépendant. Verdict d'audit du papier : `partially_holds`. Le papier le dit explicitement et propose un protocole de validation indépendante.
