#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from collections import defaultdict
from pathlib import Path

# La formule critères→score est définie une seule fois dans compute_scores.py et
# réutilisée ici : aucun risque de divergence entre génération et validation.
from compute_scores import derive_raw_from_criteria

ROOT = Path(__file__).resolve().parents[1]

# raw_score est désormais DÉRIVÉ des criteria_scores (source de vérité unique), réaligné
# par scripts/migrate_raw_from_criteria.py. La tolérance ne couvre plus qu'un éventuel
# écart d'arrondi : toute divergence réelle (raw édité à la main, critères modifiés sans
# réalignement) dépasse ce seuil et est rejetée au build.
RAW_CRITERIA_TOLERANCE = 0.5

# Groupes de critères attendus (clés de default_criteria_weights).
EXPECTED_CRITERIA_GROUPS = ('common_criteria', 'theory_specific_criteria', 'layer_specific_criteria')

# Tolérance sur le recalcul de l'internal_score de confiance (arrondi).
CONFIDENCE_TOLERANCE = 0.5


def confidence_internal_score(dimensions):
    """Recalcule l'internal_score de confiance depuis ses dimensions (cf. CONFIDENCE.md).

    Contrat unique : evidence_quality, historiographical_consensus, temporal_stability
    « positifs » ; weight_sensitivity et anachronism_risk « inversés » (100 - x).
    Retourne None si une dimension manque.
    """
    required = ('evidence_quality', 'historiographical_consensus', 'temporal_stability',
                'weight_sensitivity', 'anachronism_risk')
    if not dimensions or any(k not in dimensions for k in required):
        return None
    return round(
        0.30 * dimensions['evidence_quality']
        + 0.25 * dimensions['historiographical_consensus']
        + 0.20 * dimensions['temporal_stability']
        + 0.15 * (100 - dimensions['weight_sensitivity'])
        + 0.10 * (100 - dimensions['anachronism_risk']),
        2)


def confidence_label_for(score):
    """Label public attendu pour un internal_score donné (bandes de CONFIDENCE.md)."""
    if score < 40:
        return 'low'
    if score < 60:
        return 'medium'
    if score < 80:
        return 'high'
    return 'very_high'


def check_confidence(owner_id, confidence):
    """Gate de confiance (chantier 4c) : internal_score et label doivent découler des
    dimensions via la formule documentée. Ajoute aux `errors` toute incohérence."""
    dims = (confidence or {}).get('dimensions')
    recomputed = confidence_internal_score(dims)
    if recomputed is None:
        return  # pas de dimensions : rien à vérifier ici
    stored = confidence.get('internal_score')
    if stored is None or abs(float(stored) - recomputed) > CONFIDENCE_TOLERANCE:
        errors.append(
            f"Confidence internal_score mismatch in {owner_id}: stored={stored} "
            f"but dimensions recompute {recomputed}")
    expected_label = confidence_label_for(recomputed)
    if confidence.get('label') != expected_label:
        errors.append(
            f"Confidence label mismatch in {owner_id}: label='{confidence.get('label')}' "
            f"but internal_score {recomputed} implies '{expected_label}'")


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

errors=[]
warnings=[]

metadata = load('src/data/canonical/model_metadata.json')
criteria_weights = metadata['default_criteria_weights']
periods = {p['period_id']: p for p in load('src/data/canonical/periods.json')['periods']}
theories = {t['theory_family_id']: t for t in load('src/data/canonical/theory_taxonomy.json')['theory_families']}
evidence = {e['evidence_id']: e for e in load('src/data/canonical/evidence.json')['evidence']}
refs = {r['id']: r for r in load('src/data/canonical/references.json')['references']}
emergence = {e['theory_family_id']: e for e in load('src/data/canonical/theory_emergence.json')['emergence']}

# Toutes les familles théoriques doivent avoir une émergence déclarée (anti-anachronisme).
for tid in theories:
    if tid not in emergence:
        errors.append(f"Missing emergence data for theory family: {tid}")

CONSTRAINED_LAYERS = ('political_doctrine', 'academic_influence')

for fname in ['scores_raw.json', 'scores_entities_raw.json']:
    scores = load(f'src/data/canonical/{fname}')['scores']
    for s in scores:
        if s['period_id'] not in periods:
            errors.append(f"Unknown period_id in {s['score_id']}: {s['period_id']}")
        if s['theory_family_id'] not in theories:
            errors.append(f"Unknown theory_family_id in {s['score_id']}: {s['theory_family_id']}")
        if not (0 <= s['raw_score'] <= 100):
            errors.append(f"raw_score out of range in {s['score_id']}")
        if not s.get('evidence_basis'):
            errors.append(f"Missing evidence_basis in {s['score_id']}")
        for eid in s.get('evidence_basis', []):
            if eid not in evidence:
                warnings.append(f"Evidence id not found yet: {eid} used by {s['score_id']}")
        conf=s.get('confidence',{})
        if conf.get('label') not in ['low','medium','high','very_high']:
            errors.append(f"Invalid confidence label in {s['score_id']}")
        check_confidence(s['score_id'], conf)
        # Gates critères→score (chantier 1). Ne s'appliquent qu'aux scores actifs
        # portant des critères ; les scores rejetés (deprecated) sont exclus.
        if s.get('maturity_status') != 'deprecated':
            criteria = s.get('criteria_scores') or {}
            # 1) Structure : les trois groupes attendus doivent être présents et non vides.
            missing_groups = [g for g in EXPECTED_CRITERIA_GROUPS if not criteria.get(g)]
            if missing_groups:
                errors.append(
                    f"Criteria structure in {s['score_id']}: missing/empty groups {missing_groups}")
            else:
                # 2) Chaque valeur de critère ∈ [0, 100].
                for group_name in EXPECTED_CRITERIA_GROUPS:
                    for crit_name, crit_value in criteria[group_name].items():
                        if not (0 <= float(crit_value) <= 100):
                            errors.append(
                                f"Criterion out of range in {s['score_id']}: "
                                f"{group_name}.{crit_name} = {crit_value}")
                # 3) Cohérence : |raw_authored − raw_derived| ≤ tolérance.
                raw_derived = derive_raw_from_criteria(criteria, criteria_weights)
                if raw_derived is not None:
                    delta = abs(float(s['raw_score']) - raw_derived)
                    if delta > RAW_CRITERIA_TOLERANCE:
                        errors.append(
                            f"Raw/criteria mismatch in {s['score_id']}: raw_score="
                            f"{s['raw_score']} but criteria derive {raw_derived} "
                            f"(delta {delta:.2f} > {RAW_CRITERIA_TOLERANCE})")
        # Anti-anachronisme : un score doctrine/académique antérieur à l'émergence de la
        # théorie est interdit, sauf s'il est rejeté (deprecated) ou explicitement justifié.
        layer = s.get('layer')
        emap = emergence.get(s['theory_family_id'])
        period = periods.get(s['period_id'])
        if layer in CONSTRAINED_LAYERS and emap and period:
            if period['start_year'] < emap[f'{layer}_from']:
                if s.get('maturity_status') == 'deprecated' or s.get('anachronism_override'):
                    pass  # rejeté ou justifié : conforme à la règle
                else:
                    errors.append(
                        f"Anachronism in {s['score_id']}: {s['theory_family_id']} / {layer} "
                        f"in period starting {period['start_year']} < emergence "
                        f"{emap[f'{layer}_from']} (mark deprecated or set anachronism_override)")

# Confiance des preuves (gate 4c) + détection de templating (gate 4d).
evidence_list = load('src/data/canonical/evidence.json')['evidence']
for ev in evidence_list:
    check_confidence(ev['evidence_id'], ev.get('confidence', {}))

# Anti-templating : au sein d'une même période, plusieurs preuves partageant EXACTEMENT
# la même signature (probative_strength + dimensions de confiance) trahissent un
# copier-coller plutôt qu'une évaluation différenciée. Signalé (warning), non bloquant :
# la dette de re-sourçage est assumée tant que les données restent au stade seed.
signature_groups = defaultdict(list)
for ev in evidence_list:
    dims = (ev.get('confidence') or {}).get('dimensions') or {}
    signature = (ev.get('period_id'), ev.get('probative_strength'),
                 tuple(sorted(dims.items())))
    signature_groups[signature].append(ev['evidence_id'])
for (period_id, strength, _dims), ids in signature_groups.items():
    if len(ids) >= 3:
        warnings.append(
            f"Templating suspecté : {len(ids)} preuves de la période {period_id} partagent "
            f"probative_strength={strength} et des dimensions de confiance identiques "
            f"({', '.join(ids[:4])}{'…' if len(ids) > 4 else ''})")

# validate weights
weights = load('src/data/canonical/weight_profiles.json')['profiles']
for p in weights:
    total = sum(p['weights'].values())
    if abs(total - 1.0) > 1e-9:
        errors.append(f"Weight profile {p['profile_id']} does not sum to 1: {total}")

# validate references / bibtex keys presence
for r in refs.values():
    if not r.get('bibtex_key'):
        errors.append(f"Missing bibtex_key in reference {r['id']}")
    if not r.get('usage_tags'):
        errors.append(f"Reference without usage_tags: {r['id']}")

# Politique de maturité : reviewed/validated réservé aux périodes P1.
# (références exemptées : validées par l'audit de provenance.)
P1 = {pid for pid, p in periods.items() if p.get('priority') == 'P1'}
REVIEWED = {'reviewed', 'validated'}
maturity_targets = [
    ('src/data/canonical/scores_raw.json', 'scores', 'period_id', 'single'),
    ('src/data/canonical/scores_entities_raw.json', 'scores', 'period_id', 'single'),
    ('src/data/canonical/evidence.json', 'evidence', 'period_id', 'single'),
    ('src/data/canonical/events.json', 'events', 'period_id', 'single'),
    ('src/data/canonical/controversies.json', 'controversies', 'period_ids', 'list'),
]
def _non_p1(obj, field, kind):
    if kind == 'single':
        return obj.get(field) not in P1
    return not any(p in P1 for p in (obj.get(field) or []))
for path, key, field, kind in maturity_targets:
    for obj in load(path)[key]:
        if obj.get('maturity_status') in REVIEWED and _non_p1(obj, field, kind):
            oid = obj.get('score_id') or obj.get('evidence_id') or obj.get('event_id') or obj.get('controversy_id')
            errors.append(f"Maturity policy: {oid} is '{obj['maturity_status']}' but not in a P1 period (set to draft)")

if warnings:
    print('WARNINGS:')
    for w in warnings:
        print(' -', w)

if errors:
    print('ERRORS:')
    for e in errors:
        print(' -', e)
    sys.exit(1)

print('Validation OK')
