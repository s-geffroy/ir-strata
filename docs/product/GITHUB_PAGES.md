# GitHub Pages

## Déploiement recommandé

Le workflow `.github/workflows/deploy-pages.yml` :

1. checkout ;
2. setup Python ;
3. setup Node ;
4. validation des données ;
5. génération des dérivés ;
6. build Docusaurus ;
7. upload de l’artefact Pages ;
8. déploiement.

## Configuration à adapter

Dans `docusaurus.config.ts` :

- `organizationName`
- `projectName`
- `url`
- `baseUrl`

Pour un dépôt `username/ir-theory-historical-weighting`, le `baseUrl` est généralement `/ir-theory-historical-weighting/`.
