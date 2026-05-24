# Contribution

## Règles

1. Modifier les données dans `src/data/canonical`.
2. Ne jamais modifier à la main `src/data/generated` ou `static/exports`.
3. Ajouter une preuve pour tout score nouveau ou modifié.
4. Ajouter une entrée `revision_log` pour changement analytique majeur.
5. Lancer :

```bash
npm run validate:data
npm run build
```
