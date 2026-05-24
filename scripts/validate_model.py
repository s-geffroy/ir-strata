#!/usr/bin/env python3
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

errors=[]
warnings=[]

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
