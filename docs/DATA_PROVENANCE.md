---
id: DATA_PROVENANCE
title: Provenance des données
sidebar_label: Provenance des données
---

# Provenance et fiabilité des données

> **Statut : seed généré, non vérifié, à re-sourcer.** `source_status: draft_unverified_seed`

## Ce que sont les données fournies

Le jeu de données canoniques livré avec ir-strata (scores bruts, preuves,
événements, controverses, références bibliographiques) est un **seed de départ
généré**. Il n'a **pas été vérifié** contre les sources primaires ou secondaires
réelles.

Concrètement, à ce stade :

- les **scores** n'ont pas de justification empirique validée par un expert ;
- les **références bibliographiques** n'ont pas été confirmées comme existantes
  (risque d'ouvrages ou de clés `bibtex` hallucinés) ;
- les **preuves** et **controverses** sont structurellement valides mais non auditées.

## À quoi il sert

Ce seed sert **uniquement** à :

1. faire fonctionner la chaîne technique (validation → calcul → exports → site) ;
2. démontrer le format des données et l'interface ;
3. servir de gabarit à remplir avec des données réellement sourcées.

Il **ne constitue pas** une autorité historique, ni une mesure objective, ni une
position académique défendable en l'état.

## Ce qui a été fait

- **Audit de provenance des références (anti-hallucination)** : `scripts/audit_references.py`
  interroge Crossref et OpenLibrary pour retrouver chaque référence dans des bases réelles.
  Résultat : **56/56 références vérifiées, 0 hallucination détectée** (voir
  [Audit des références](AUDIT_REFERENCES)).
- **Anti-anachronisme automatisé** : table d'émergence + détection + rejet ; **446 scores
  anachroniques rejetés** (voir [Audit anti-anachronisme](AUDIT_ANACHRONISM)). Garde au build.
- **Découplage de la synthèse** et **non-exclusivité** : les trois couches sont affichées
  séparément, le brut est consultable, la synthèse est explicitement présentée comme dérivée
  et dépendante de la pondération.
- **Politique de maturité** : `reviewed`/`validated` réservé aux périodes prioritaires P1
  (`scripts/enforce_maturity_policy.py`, garde au build). Tout objet hors P1 est `draft`.
  Les scores d'entités sont tous `draft`. Seules les références restent `reviewed` (vérifiées).

## Ce qui reste prévu (phases ultérieures)

- Re-sourçage et calibration des **scores** eux-mêmes (les audits valident l'existence des
  références et la non-anachronicité, pas la justesse des valeurs de score), en commençant
  par les périodes P1.

## Règle

Tant que `source_status` n'est pas passé à un statut vérifié, **aucun chiffre de ce
site ne doit être cité comme un fait**.
