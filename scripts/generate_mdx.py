#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))

tax=load('src/data/canonical/theory_taxonomy.json')['theory_families']
labels={t['theory_family_id']: t['label_fr'] for t in tax}
periods=load('src/data/canonical/periods.json')['periods']
scores=load('src/data/generated/scores_synthesis_normalized.json')['scores']
events=load('src/data/canonical/events.json')['events']
controversies=load('src/data/canonical/controversies.json')['controversies']

outdir=ROOT/'docs/periods'; outdir.mkdir(parents=True, exist_ok=True)
for p in periods:
    pid=p['period_id']
    rows=sorted([r for r in scores if r['period_id']==pid and r['entity_id']=='global_system' and r['layer']=='synthesis'], key=lambda x:x['normalized_score'], reverse=True)
    md=[f"# {p['label']} — {p['title_fr']}", "", f"**Priorité :** `{p['priority']}`  ", f"**Maturité :** `{p['maturity_status']}`", "", "## Synthèse", "", p.get('summary_fr',''), "", "## Scores globaux synthétiques", "", "| Théorie | Score brut | Score normalisé | Confiance |", "|---|---:|---:|---|"]
    for r in rows:
        conf=(r.get('confidence') or {}).get('label','')
        md.append(f"| {labels.get(r['theory_family_id'], r['theory_family_id'])} | {r['raw_score']} | {r['normalized_score']:.2f}% | {conf} |")
    md += ["", "## Événements-pivots", ""]
    evs=[e for e in events if e['period_id']==pid]
    md += [f"- **{e['year']}** — {e['label_fr']} (`{e['event_type']}`)" for e in evs] or ["- Aucun événement-pivot structuré en V1."]
    md += ["", "## Controverses", ""]
    cont=[c for c in controversies if pid in c['period_ids']]
    md += [f"- **{c['label_fr']}** — décision modèle : {c['model_decision']}" for c in cont] or ["- Aucune controverse structurée en V1."]
    md += ["", "## Note méthodologique", "", "Cette page est générée depuis les données canoniques."]
    (outdir/f"{p['label']}.md").write_text("\n".join(md)+"\n", encoding='utf-8')
print('MDX docs generated')
