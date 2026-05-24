# Anti-anachronisme

Une théorie moderne peut être utilisée rétrospectivement pour analyser une réalité stratégique ancienne, mais elle ne peut pas compter comme doctrine ou influence académique avant son émergence.

## Règle

| Couche | Règle |
|---|---|
| `strategic_reality` | Usage rétrospectif autorisé si phénomène réel. |
| `political_doctrine` | Seulement idées disponibles pour les acteurs de l’époque. |
| `academic_influence` | Seulement théories formalisées ou débats académiques existants. |

Exemple : le constructivisme peut aider à lire la souveraineté de 1815 rétrospectivement, mais ne peut pas scorer comme école académique en 1815.

## Mécanisme automatisé

La règle n'est plus seulement documentaire : elle est outillée et appliquée au build.

1. **Données d'émergence** — `src/data/canonical/theory_emergence.json` déclare, par famille
   théorique, l'année d'émergence pour `political_doctrine` et `academic_influence` (avec
   justification). `strategic_reality` n'est jamais contrainte.
2. **Détection** — `scripts/audit_anachronism.py` confronte chaque score de ces deux couches
   à l'émergence. Rapport : `docs/AUDIT_ANACHRONISM.md` (lisible) + `references/anachronism_report.json`.
3. **Rejet** — `--write` passe les scores fautifs en `maturity_status: deprecated` (avec un
   bloc `anachronism`). `compute_scores.py` les exclut alors des scores normalisés, de la
   synthèse et des graphiques. Un usage anachronique délibérément assumé peut être conservé
   en portant `anachronism_override: true`.
4. **Garde au build** — `scripts/validate_model.py` échoue si un score doctrine/académique
   antérieur à l'émergence n'est ni rejeté (`deprecated`) ni justifié (`anachronism_override`).

Conséquence assumée : la couche `academic_influence` est vide pour les périodes antérieures
à l'existence d'une science des RI (avant ~1890-1919) et se peuple à mesure que les écoles
émergent ; la synthèse pondérée, qui requiert les trois couches, n'est donc disponible que
là où elles coexistent légitimement.
