# Scoring

## Score brut

Le score brut est la donnée analytique canonique.

```text
score_brut = critères communs + critères spécifiques + critères par couche + preuves + confiance
```

## Score normalisé

Le score normalisé est généré :

```text
score_normalisé(théorie) = raw_score(théorie) / somme(raw_scores du groupe) × 100
```

### Limite : non-exclusivité et non-exhaustivité

La normalisation à 100 % suppose implicitement que les familles théoriques sont
**mutuellement exclusives et exhaustives**. Elles ne le sont pas : réalisme, libéralisme,
constructivisme, etc. se chevauchent et n'épuisent pas le réel. Un score normalisé est donc
une **part relative dans l'ensemble de théories retenu**, jamais une « part du monde ».

En conséquence :

- le **score brut** (intensité analytique indépendante, 0-100) est la donnée canonique et
  doit rester consultable partout ;
- l'interface propose une bascule **Brut / Normalisé** ; le mode brut est rendu en lignes
  **non empilées** pour rappeler que les intensités sont indépendantes et peuvent se
  chevaucher ;
- les vues normalisées portent un avertissement explicite de non-exclusivité.

## Pondération des critères

Défaut V1 :

```json
{
  "common_criteria": 0.25,
  "theory_specific_criteria": 0.40,
  "layer_specific_criteria": 0.35
}
```

## Synthèse

Défaut V1 :

```json
{
  "strategic_reality": 0.60,
  "political_doctrine": 0.25,
  "academic_influence": 0.15
}
```

Les poids sont modifiables dans l’interface, mais toute variation forte doit afficher l’écart avec le profil par défaut.
