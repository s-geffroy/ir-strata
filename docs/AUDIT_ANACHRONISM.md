---
id: AUDIT_ANACHRONISM
title: Audit anti-anachronisme
sidebar_label: Audit anti-anachronisme
---

# Audit anti-anachronisme

_Audité le 2026-05-24._

Confronte les scores des couches `political_doctrine` et `academic_influence` aux années d'émergence (`theory_emergence.json`). La couche `strategic_reality` n'est jamais contrainte (usage rétrospectif autorisé). Les scores fautifs non justifiés sont rejetés (`maturity_status: deprecated`) et exclus des graphiques.

## Synthèse

- Scores anachroniques détectés : **446**
- Dont déjà rejetés / justifiés : 446
- Rejetés par cet audit (`--write`) : 0

### Par couche

| Couche | Nombre |
| --- | --- |
| `academic_influence` | 272 |
| `political_doctrine` | 174 |

### Par famille théorique

| Famille | Nombre |
| --- | --- |
| `constructivism` | 126 |
| `critical_postcolonial_feminist` | 113 |
| `english_school` | 102 |
| `realism` | 32 |
| `marxism_dependency_structuralism` | 30 |
| `liberalism` | 22 |
| `geopolitics_imperialism_reason_of_state` | 21 |

## Exemples (jusqu'à 25)

| score_id | famille | couche | période début | émergence | années avant |
| --- | --- | --- | --- | --- | --- |
| `score_1815_1848_global_system_political_doctrine_marxism_dependency_structuralism` | marxism_dependency_structuralism | political_doctrine | 1815 | 1848 | 33 |
| `score_1815_1848_global_system_political_doctrine_constructivism` | constructivism | political_doctrine | 1815 | 1989 | 174 |
| `score_1815_1848_global_system_political_doctrine_english_school` | english_school | political_doctrine | 1815 | 1959 | 144 |
| `score_1815_1848_global_system_political_doctrine_critical_postcolonial_feminist` | critical_postcolonial_feminist | political_doctrine | 1815 | 1961 | 146 |
| `score_1815_1848_global_system_academic_influence_realism` | realism | academic_influence | 1815 | 1939 | 124 |
| `score_1815_1848_global_system_academic_influence_liberalism` | liberalism | academic_influence | 1815 | 1919 | 104 |
| `score_1815_1848_global_system_academic_influence_marxism_dependency_structuralism` | marxism_dependency_structuralism | academic_influence | 1815 | 1902 | 87 |
| `score_1815_1848_global_system_academic_influence_constructivism` | constructivism | academic_influence | 1815 | 1989 | 174 |
| `score_1815_1848_global_system_academic_influence_english_school` | english_school | academic_influence | 1815 | 1959 | 144 |
| `score_1815_1848_global_system_academic_influence_critical_postcolonial_feminist` | critical_postcolonial_feminist | academic_influence | 1815 | 1978 | 163 |
| `score_1815_1848_global_system_academic_influence_geopolitics_imperialism_reason_of_state` | geopolitics_imperialism_reason_of_state | academic_influence | 1815 | 1890 | 75 |
| `score_1848_1871_global_system_political_doctrine_constructivism` | constructivism | political_doctrine | 1848 | 1989 | 141 |
| `score_1848_1871_global_system_political_doctrine_english_school` | english_school | political_doctrine | 1848 | 1959 | 111 |
| `score_1848_1871_global_system_political_doctrine_critical_postcolonial_feminist` | critical_postcolonial_feminist | political_doctrine | 1848 | 1961 | 113 |
| `score_1848_1871_global_system_academic_influence_realism` | realism | academic_influence | 1848 | 1939 | 91 |
| `score_1848_1871_global_system_academic_influence_liberalism` | liberalism | academic_influence | 1848 | 1919 | 71 |
| `score_1848_1871_global_system_academic_influence_marxism_dependency_structuralism` | marxism_dependency_structuralism | academic_influence | 1848 | 1902 | 54 |
| `score_1848_1871_global_system_academic_influence_constructivism` | constructivism | academic_influence | 1848 | 1989 | 141 |
| `score_1848_1871_global_system_academic_influence_english_school` | english_school | academic_influence | 1848 | 1959 | 111 |
| `score_1848_1871_global_system_academic_influence_critical_postcolonial_feminist` | critical_postcolonial_feminist | academic_influence | 1848 | 1978 | 130 |
| `score_1848_1871_global_system_academic_influence_geopolitics_imperialism_reason_of_state` | geopolitics_imperialism_reason_of_state | academic_influence | 1848 | 1890 | 42 |
| `score_1871_1914_global_system_political_doctrine_constructivism` | constructivism | political_doctrine | 1871 | 1989 | 118 |
| `score_1871_1914_global_system_political_doctrine_english_school` | english_school | political_doctrine | 1871 | 1959 | 88 |
| `score_1871_1914_global_system_political_doctrine_critical_postcolonial_feminist` | critical_postcolonial_feminist | political_doctrine | 1871 | 1961 | 90 |
| `score_1871_1914_global_system_academic_influence_realism` | realism | academic_influence | 1871 | 1939 | 68 |
