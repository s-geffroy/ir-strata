# Pipeline de build

Deux pistes distinctes : le **build** (déterministe, sans mutation, sans réseau pour le cœur)
et le **rafraîchissement des données** (passes mutantes, à la demande).

## Build (déterministe)

```text
canonical JSON
→ validate_model.py        (gardes : scores 0-100, poids, refs, anti-anachronisme, maturité P1)
→ compute_scores.py
→ generate_exports.py
→ generate_mdx.py
→ docusaurus build
→ GitHub Pages
```

`validate_model.py` est la **garde au build** : il échoue si une donnée viole une règle
(anachronisme non rejeté, `reviewed` hors P1, score hors borne…). Les gardes anachronisme et
maturité sont déterministes et hors réseau.

## Vérifications (read-only)

- `npm run check:data` — validate + `audit_anachronism --check` + `enforce_maturity_policy --check`
  (hors réseau, utilisable partout).
- `npm run audit:refs` — `audit_references --check` (réseau : Crossref/OpenLibrary). Exécuté en
  CI où le réseau est disponible ; échoue si une référence devient non vérifiable.

## Rafraîchissement des données (mutant, à la demande)

```text
npm run data:refresh
= audit_anachronism.py --write      (rejette les anachronismes -> deprecated)
+ enforce_maturity_policy.py --write (reviewed réservé aux P1)
+ audit_references.py --write        (flag les refs non vérifiables)
+ build_site.py                      (régénère les artefacts)
```

À lancer après toute modification des données canoniques. Ne fait pas partie du build CI :
il modifie les fichiers canoniques (et touche le réseau pour les références).

## CI

Le workflow GitHub Actions exécute, avant le build : `check:data` (gardes hors ligne) puis
`audit:refs` (réseau). Aucun fichier généré ne doit être modifié à la main.
