#!/usr/bin/env python3
from __future__ import annotations
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def write_csv(path, rows, fields):
    p=ROOT/path; p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows: w.writerow({k:r.get(k,'') for k in fields})

scores=load('src/data/generated/scores_synthesis_normalized.json')['scores']
annual=load('src/data/generated/annual_interpolated_scores.json')['scores']
write_csv('static/exports/scores_global.csv', [r for r in scores if r['entity_id']=='global_system'], ['period_id','entity_id','scope','layer','theory_family_id','raw_score','normalized_score','maturity_status'])
write_csv('static/exports/scores_entities.csv', [r for r in scores if r['entity_id']!='global_system'], ['period_id','entity_id','scope','layer','theory_family_id','raw_score','normalized_score','maturity_status'])
write_csv('static/exports/annual_interpolated_scores.csv', annual, ['year','period_id','entity_id','scope','layer','theory_family_id','raw_score','normalized_score','confidence_label','derivation_status'])
print('Exports generated')
