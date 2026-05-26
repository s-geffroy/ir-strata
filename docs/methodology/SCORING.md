# Scoring

## Score brut

Le score brut n'est **plus** saisi à la main : il est **dérivé déterministiquement des
critères** (la donnée canonique de base, avec preuves et confiance). La formule appliquée
est la moyenne de chaque groupe de critères, pondérée par les poids de critères :

```text
raw_score = 0.25 × moyenne(critères communs)
          + 0.40 × moyenne(critères spécifiques à la théorie)
          + 0.35 × moyenne(critères propres à la couche)
```

(poids = `model_metadata.json:default_criteria_weights`.)

Conséquences :

- les **critères** (`criteria_scores`) sont la **source de vérité unique** ; modifier un
  score = modifier ses critères, pas le `raw_score` ;
- `raw_score` est réaligné par `scripts/migrate_raw_from_criteria.py` et **vérifié par un
  gate** (`validate_model.py`) : tout `raw_score` qui diverge de ses critères au-delà de la
  tolérance d'arrondi fait échouer le build ;
- l'implémentation de référence est `compute_scores.derive_raw_from_criteria` (Python),
  mirroirée côté client par `deriveRawFromCriteria` dans `src/utils/scoring.ts`.

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

- le **score brut** (intensité analytique indépendante, 0-100, dérivé des critères) doit
  rester consultable partout ;
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
