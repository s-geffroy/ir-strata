---
id: CALIBRATION_STATUS
title: Avancement du re-sourçage
sidebar_label: Re-sourçage des scores
---

# Avancement du re-sourçage des scores

_État au 2026-05-26._

> **Ce que « sourcé » garantit — et ne garantit pas.** Le statut `sourced` signifie que le score est **adossé à des preuves et des références vérifiées** (existantes, non anachroniques). Il ne signifie **pas** que la valeur numérique est validée empiriquement par un spécialiste : cette validation relève de l'étude inter-codeurs (voir la console de codage et le rapport inter-codeurs).

Le re-sourçage remplace progressivement les justifications seed par des justifications réelles, adossées aux preuves et références vérifiées. Ce tableau en mesure l'avancement.

**1549 / 1549 scores _actifs_ re-sourcés (100.0 %).**

_Le total inclut aussi 446 scores rejetés pour anachronisme (`deprecated`), exclus de ce décompte : « 100 % » se lit donc « 100 % des scores actifs adossés à des preuves », pas « 100 % validés »._

## Par période (priorité P1 d'abord)

| Période | Priorité | Sourcé | Seed |
| --- | --- | ---: | ---: |
| 1815_1848 | P1 | 90 | 0 |
| 1871_1914 | P1 | 121 | 0 |
| 1919_1939 | P1 | 140 | 0 |
| 1939_1945 | P1 | 135 | 0 |
| 1945_1962 | P1 | 150 | 0 |
| 1962_1979 | P1 | 198 | 0 |
| 1991_2001 | P1 | 189 | 0 |
| 2014_2022 | P1 | 210 | 0 |
| 2022_2026 | P1 | 231 | 0 |
| 1848_1871 | P2 | 11 | 0 |
| 1914_1919 | P2 | 13 | 0 |
| 1979_1991 | P2 | 19 | 0 |
| 2001_2008 | P2 | 21 | 0 |
| 2008_2014 | P2 | 21 | 0 |

## Dette : preuves encore au stade gabarit

**48 / 48 preuves** portent encore un résumé gabarit (« À enrichir avec citations précises »). Tant que ce compteur n'est pas nul, le `probative_strength` de ces preuves reste indicatif, non documenté.

| Preuve | Période |
| --- | --- |
| vienna_congress_1815 | 1815_1848 |
| concert_europe_balance | 1815_1848 |
| colonial_imperial_continuity | 1815_1848 |
| revolutions_1848 | 1848_1871 |
| national_unifications | 1848_1871 |
| crimean_war_balance | 1848_1871 |
| imperial_partition_competition | 1871_1914 |
| naval_arms_race | 1871_1914 |
| alliance_systems_pre_1914 | 1871_1914 |
| world_war_one_total_war | 1914_1919 |
| empire_collapse_1918 | 1914_1919 |
| wilsonian_moment_1919 | 1914_1919 |
| versailles_order | 1919_1939 |
| league_of_nations_security | 1919_1939 |
| great_depression_international_order | 1919_1939 |
| revisionist_powers_1930s | 1919_1939 |
| world_war_two_total_war | 1939_1945 |
| axis_imperial_projects | 1939_1945 |
| allied_grand_strategy | 1939_1945 |
| united_nations_1945 | 1939_1945 |
| cold_war_bipolarity_1945_1962 | 1945_1962 |
| bretton_woods_institutional_order | 1945_1962 |
| decolonization_initial_wave | 1945_1962 |
| nuclear_deterrence_emergence | 1945_1962 |
| cold_war_detente | 1962_1979 |
| non_aligned_and_bandung_legacy | 1962_1979 |
| dependency_and_oil_shocks | 1962_1979 |
| postcolonial_sovereignty_expansion | 1962_1979 |
| second_cold_war | 1979_1991 |
| soviet_crisis_and_reform | 1979_1991 |
| neoliberal_turn | 1979_1991 |
| end_of_cold_war | 1979_1991 |
| us_unipolarity_1991_2001 | 1991_2001 |
| liberal_institutional_expansion_1991_2001 | 1991_2001 |
| humanitarian_intervention_norms_1990s | 1991_2001 |
| september_11_and_war_on_terror | 2001_2008 |
| iraq_war_2003 | 2001_2008 |
| security_exceptionalism_2000s | 2001_2008 |
| global_financial_crisis_2008 | 2008_2014 |
| arab_uprisings_2011 | 2008_2014 |
| crimea_donbass_2014 | 2008_2014 |
| russia_west_fragmentation_2014_2022 | 2014_2022 |
| us_china_rivalry_acceleration | 2014_2022 |
| sanctions_and_hybrid_conflict | 2014_2022 |
| ukraine_invasion_2022 | 2022_2026 |
| sanctions_energy_security_2022_2026 | 2022_2026 |
| bloc_flexibility_global_south | 2022_2026 |
| indo_pacific_security_rivalry | 2022_2026 |

## Méthode de re-sourçage

Pour chaque score : justification analytique réelle, `evidence_basis` pointant des preuves existantes, `direct_references` vers des références **vérifiées**, confiance recalibrée, `known_limits` explicites, puis `calibration_status: "sourced"`. Voir la tranche déjà traitée comme gabarit (1945-1962, couche `strategic_reality`).
