# Codebook synthétique — Strates RI

## Statut des scores

Les scores 0-100 sont des quasi-intervalles interprétatifs. Ils ne doivent pas être lus comme mesures cardinales fortes.

## Ancres générales

| Score | Interprétation |
|---:|---|
| 0-20 | Pertinence absente, marginale ou anachronique sans capacité discriminante. |
| 21-40 | Pertinence faible ou locale. |
| 41-60 | Pertinence moyenne ; explique une dimension significative mais non dominante. |
| 61-80 | Pertinence forte ; explique des structures répétées et documentées. |
| 81-100 | Pertinence centrale, systémique, probante et discriminante. |

## Couches

| Couche | Sources admissibles |
|---|---|
| strategic_reality | guerres, alliances, capacités, polarité, institutions effectives, flux, empires, infrastructures, crises |
| political_doctrine | discours, doctrines d'État, traités, stratégies, doctrines militaires, votes, pratiques institutionnelles |
| academic_influence | ouvrages, articles, manuels, débats disciplinaires, écoles de pensée, réception académique |

## Anti-anachronisme (règle d'application stricte)

`strategic_reality` autorise toujours la lecture rétrospective d'une théorie (avec un `anachronism_risk` croissant avec l'écart à l'émergence des idées). En revanche, sur `political_doctrine` et `academic_influence`, une théorie **non encore émergée** à la période ne reçoit pas un score faible : elle est **rejetée** (statut `deprecated`, motif anachronisme) et **exclue** de la normalisation, de la synthèse et des graphiques. Une synthèse n'est calculée que pour les familles présentes sur les trois couches. Un usage anachronique délibérément assumé peut être conservé via un marqueur d'override explicite.

Années d'émergence indicatives (couche académique) : réalisme ~1939, libéralisme ~1919, marxisme/IPE ~1902, géopolitique ~1890, École anglaise ~1959, critiques/postcoloniales/féministes ~1978, constructivisme ~1989.

## Validation inter-codeurs proposée

- 3 codeurs
- 3 périodes pilotes : 1815-1848, 1945-1962, 1991-2001
- 7 familles x 3 couches x 3 périodes = 63 scores par codeur
- seuil acceptable : écart absolu moyen <= 10 points
- 11-15 points : discussion obligatoire
- >15 points : statut contested
