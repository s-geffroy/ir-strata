# Agrégation global / entités

Le score global expert n’est pas une moyenne mécanique des entités.

Pour les périodes P1 :

1. score global expert ;
2. profils d’entités pondérées ;
3. agrégation pondérée ;
4. analyse des divergences ;
5. audit.

## Divergence

| Écart | Statut |
|---:|---|
| 0-5 | coherent |
| 6-12 | acceptable_divergence |
| 13-20 | review_needed |
| >20 | strong_divergence |

## Découplage des couches et statut de la synthèse

Les trois couches — `strategic_reality`, `political_doctrine`, `academic_influence` —
mesurent des dimensions **non commensurables** : la réalité stratégique est une lecture
rétrospective, la doctrine est ce qui était assumé à l'époque, l'influence académique est
la diffusion savante. Les additionner en un seul nombre relève d'une **convention**, pas
d'une mesure.

En conséquence :

- chaque couche est **normalisée séparément** (`scores_normalized.json`) et affichée pour
  elle-même ; c'est la **vue par défaut** ;
- la **synthèse pondérée** (`scores_synthesis_normalized.json`, défaut 60 / 25 / 15) est un
  **construit dérivé**, jamais présenté comme une vérité unique ;
- l'**incertitude d'agrégation** est explicitée : `scores_synthesis_sensitivity.json`
  recalcule la synthèse sous chacun des profils de `weight_profiles.json` et expose
  `min` / `max` / `spread`. Un écart large = un chiffre agrégé peu robuste.

Ces artefacts sont générés par `scripts/compute_scores.py` à partir des scores bruts
canoniques (aucune valeur de synthèse n'est stockée comme source canonique).
