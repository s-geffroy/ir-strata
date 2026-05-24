# Strates RI — Papier Chemin A

Ce dossier contient une version réorientée vers le **chemin A : article académique / working paper sérieux**.

## Fichiers

- `papier_strates_ri_chemin_a.txt` : **source unique** de l'article (LaTeX inline avec `\citep`).
- `references_strates_ri_chemin_a.bib` : bibliographie BibTeX.
- `annexe_pilot_scores_1945_1962.csv` : scores pilotes (alignés sur l'atlas).
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

Le cas 1945--1962 est un **codage pilote auteur unique**. Il démontre l'applicabilité du protocole, mais ne prouve pas encore la fiabilité inter-codeurs. Le papier le dit explicitement et propose un protocole de validation indépendante.
