---
id: SPECIALIST_VALIDATION
title: Validation par des spécialistes RI
sidebar_label: Validation spécialistes
---

# Validation par des spécialistes des relations internationales

Les garde-fous automatiques (anti-anachronisme, audit de références, cohérence
critères→score, alignement bibliométrique) rendent le modèle **interne­ment cohérent et
falsifiable**, mais ne valident pas la **justesse** des valeurs. Cette validation relève
d’un re-codage indépendant par des spécialistes. Cette page décrit le protocole.

## Principe

Un·e spécialiste re-code **à l’aveugle** le sous-ensemble protocole (périodes pilotes ×
7 familles × 3 couches), sans voir les scores de l’auteur. On mesure ensuite l’accord
inter-codeurs (MAE, ICC(3,1), α de Krippendorff) — voir [Fiabilité
inter-codeurs](./INTERCODER.md).

## Procédure

1. **Codage à l’aveugle.** Ouvrir la [console de codage](/coding-console). Pour chaque
   score, seuls le contexte (période, couche, famille, preuves) sont montrés ; le score de
   l’auteur est masqué. Saisir les critères (0–100) ; le score brut est calculé en direct
   par la formule documentée (cf. [Scoring](./SCORING.md)).
2. **Export.** En fin de codage, exporter le fichier `coder_<id>.json` (identifiant
   anonyme). L’avancement est sauvegardé localement (navigateur) entre les sessions.
3. **Dépôt.** Transmettre le fichier au mainteneur, qui le place dans
   `src/data/coders/` puis relance `python3 scripts/intercoder_reliability_test.py`.
4. **Lecture du rapport.** Le rapport inter-codeurs se met à jour : MAE par bloc, ICC(3,1),
   α de Krippendorff. Seuil d’accord visé : **MAE ≤ 10** par bloc (période × couche).
5. **Réconciliation.** Pour tout bloc au-dessus du seuil, examiner les écarts (le codebook
   ou les bornes de période sont à revoir) ; toute révision de score est journalisée dans
   `revision_log.json` (cf. `scripts/track_revisions.py`).

## Statut et conséquences

- Tant qu’aucun codage indépendant n’est déposé, les données restent étiquetées
  `draft_unverified_seed` : la fiabilité inter-codeurs n’est **pas** testable.
- Le passage d’un score en `reviewed`/`validated` (périodes P1 uniquement) suppose un
  accord inter-codeurs sous le seuil pour le bloc concerné.
- Le re-codage porte sur les **critères**, source de vérité unique ; le score brut en
  découle automatiquement.
