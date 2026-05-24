# Prompt d’implémentation pour agent de code

Tu es un agent de code senior. Ta tâche est d’implémenter, tester et durcir ce projet Docusaurus/GitHub Pages.

## Objectif

Finaliser un atlas analytique statique intitulé : “Pondération historique des théories des relations internationales”.

## Contraintes non négociables

1. Le JSON canonique reste la source de vérité.
2. Les scores normalisés sont générés, jamais édités à la main.
3. Les pages période sont générées depuis les données.
4. Le site doit fonctionner sur GitHub Pages sans backend.
5. Les poids utilisateur sont recalculés côté navigateur uniquement.
6. Le build échoue si les données critiques sont incohérentes.
7. Les objets `deprecated` ne doivent pas alimenter les exports publics.
8. Les objets `draft` doivent être visibles avec badge.
9. Les références doivent rester synchronisées entre JSON, BibTeX et Markdown.

## Étapes d’implémentation

1. Installer les dépendances.
2. Lancer `npm run validate:data` et corriger les erreurs.
3. Compléter les schémas JSON avec contraintes strictes.
4. Durcir `scripts/validate_model.py`.
5. Vérifier `scripts/compute_scores.py`.
6. Améliorer les composants React pour états vides et erreurs.
7. Vérifier que `npm run build` produit un site statique propre.
8. Tester le workflow GitHub Actions.
9. Ajouter un guide de contribution.
10. Ne pas inventer de nouveaux scores analytiques sans les marquer `draft` et sans preuve.

## Livrable attendu

Un dépôt qui peut être poussé sur GitHub et publié via GitHub Pages.
