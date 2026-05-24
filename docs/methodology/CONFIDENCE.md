# Confiance et incertitude

La confiance combine un label public et des dimensions internes.

## Dimensions

- `evidence_quality`
- `historiographical_consensus`
- `temporal_stability`
- `weight_sensitivity`
- `anachronism_risk`

## Formule recommandée

```text
confidence_internal_score =
0.30 × evidence_quality
+ 0.25 × historiographical_consensus
+ 0.20 × temporal_stability
+ 0.15 × (100 - weight_sensitivity)
+ 0.10 × (100 - anachronism_risk)
```

## Labels

| Score | Label |
|---:|---|
| 0-39 | low |
| 40-59 | medium |
| 60-79 | high |
| 80-100 | very_high |
