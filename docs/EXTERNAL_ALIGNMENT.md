---
id: EXTERNAL_ALIGNMENT
title: Alignement au signal externe
sidebar_label: Alignement externe
---

# Alignement de l'influence académique au signal bibliométrique externe

_État au 2026-05-26._

Corrélation de rang (Spearman) entre les scores `academic_influence` normalisés du modèle et un **signal externe indépendant** (comptes de publications OpenAlex par famille, cf. `build_external_signal.py`). Le signal est un **proxy** : une corrélation faible invite au réexamen, elle ne prouve pas une erreur.

Seuil d'alerte : Spearman < 0.3.

| Période | Familles | Spearman | Statut |
| --- | ---: | ---: | --- |
| 1919_1939 | 3 | 0.866 | ok |
| 1939_1945 | 4 | 0.316 | ok |
| 1945_1962 | 4 | 0.800 | ok |
| 1962_1979 | 5 | 0.100 | ⚠️ à réexaminer |
| 1979_1991 | 6 | 0.087 | ⚠️ à réexaminer |
| 1991_2001 | 7 | 0.429 | ok |
| 2001_2008 | 7 | 0.505 | ok |
| 2008_2014 | 7 | 0.143 | ⚠️ à réexaminer |
| 2014_2022 | 7 | 0.071 | ⚠️ à réexaminer |
| 2022_2026 | 7 | 0.107 | ⚠️ à réexaminer |
