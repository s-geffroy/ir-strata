#!/usr/bin/env python3
"""Génère les artefacts CSV du pilote du papier (paper/annexe_pilot_*.csv).

Tous les chiffres sont DÉRIVÉS des données canoniques et générées — aucun n'est saisi
à la main. C'est ce script qui rend vraie la revendication de reproductibilité du
papier : les tables de `paper/main.tex` doivent toutes se retrouver dans ces CSV.

Sources :
- src/data/canonical/scores_raw.json          (scores bruts par couche + maturité)
- src/data/canonical/theory_taxonomy.json      (familles, ordre, libellés)
- src/data/canonical/theory_emergence.json     (années d'émergence, notes anachronisme)
- src/data/generated/scores_synthesis_raw.json            (synthèse brute)
- src/data/generated/scores_synthesis_normalized.json     (part normalisée)
- src/data/generated/scores_synthesis_sensitivity_raw.json (sensibilité brute + statut)

Sorties dans paper/ : annexe_pilot_scores_<periode>.csv (3), annexe_pilot_sensitivity.csv,
annexe_pilot_intercoder_simulation.csv.

stdlib uniquement.
"""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Périodes du pilote, dans l'ordre du papier.
PILOT_PERIODS = ['1815_1848', '1945_1962', '1991_2001']

# Couches doctrine/académique soumises à l'anti-anachronisme (la couche stratégique
# est toujours admise au titre d'une lecture rétrospective).
LAYER_LABELS = {'political_doctrine': 'doctrine', 'academic_influence': 'academique'}

# Règle déterministe et déclarée de la simulation de second codage (cf. papier) :
SIM_DOMINANT_DISCOUNT = 8   # méfiance envers la lecture dominante
SIM_PERIPHERAL_RAISE = 6    # sous-pondération supposée des hiérarchies mondiales
SIM_REALISM_DISCOUNT = 5    # méfiance envers le primat de la puissance (si non dominant)
SIM_RAISE_FAMILIES = {'marxism_dependency_structuralism', 'critical_postcolonial_feminist'}


def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def write_csv(path, rows, fields):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, '') for k in fields})


def num(x):
    """Format numérique stable pour CSV : '' si None, sinon arrondi à 2 décimales sans
    zéros parasites (90.40 -> '90.4', 93.25 -> '93.25')."""
    if x is None:
        return ''
    return f'{round(float(x), 2):g}'


def difference_status(abs_diff):
    """Statut d'accord inter-codeurs selon le codebook : aligné (<=10), discussion
    (11-15), contested (>15)."""
    if abs_diff <= 10:
        return 'aligned'
    if abs_diff <= 15:
        return 'discussion'
    return 'contested'


def anachronism_note(rejected_layers, academic_from, period_has_synthesis):
    """Note explicative pour une famille dont une couche est rejetée (deprecated)."""
    if not rejected_layers:
        return ''
    labels = [LAYER_LABELS[l] for l in rejected_layers]
    verbe = 'rejetees' if len(labels) > 1 else 'rejetee'
    note = f"{' et '.join(labels)} {verbe} (anachronisme ; emergence academique vers {academic_from})"
    if not period_has_synthesis:
        note += ' ; pas de synthese pour cette periode'
    return note


def main():
    raw = load('src/data/canonical/scores_raw.json')['scores']
    taxonomy = load('src/data/canonical/theory_taxonomy.json')['theory_families']
    emergence = {e['theory_family_id']: e
                 for e in load('src/data/canonical/theory_emergence.json')['emergence']}
    synth_raw = load('src/data/generated/scores_synthesis_raw.json')['scores']
    synth_norm = load('src/data/generated/scores_synthesis_normalized.json')['scores']
    sens_raw = load('src/data/generated/scores_synthesis_sensitivity_raw.json')['scores']
    profiles = load('src/data/canonical/weight_profiles.json')['profiles']
    entities = {e['entity_id']: e for e in load('src/data/canonical/entities.json')['entities']}

    family_order = [f['theory_family_id'] for f in taxonomy]
    family_index = {fid: i for i, fid in enumerate(family_order)}

    # Lookups (global_system / scope global uniquement).
    def is_global(s):
        return s.get('entity_id') == 'global_system' and s.get('scope') == 'global'

    layer_raw = {}      # (pid, fam, layer) -> (raw_score, maturity_status)
    for s in raw:
        if is_global(s):
            layer_raw[(s['period_id'], s['theory_family_id'], s['layer'])] = (
                s['raw_score'], s.get('maturity_status'))
    synth_raw_by = {(s['period_id'], s['theory_family_id']): s['raw_score']
                    for s in synth_raw if is_global(s)}
    synth_norm_by = {(s['period_id'], s['theory_family_id']): s['normalized_score']
                     for s in synth_norm if is_global(s)}
    sens_by = {(s['period_id'], s['theory_family_id']): s for s in sens_raw}
    periods_with_synthesis = {pid for (pid, _fam) in synth_raw_by}

    # Lookups par entité (scope global ET entité) — pour la déclinaison C4.
    synth_raw_ent = {(s['period_id'], s['entity_id'], s['theory_family_id']): s['raw_score']
                     for s in synth_raw if s.get('scope') in ('global', 'entity')}
    synth_norm_ent = {(s['period_id'], s['entity_id'], s['theory_family_id']): s['normalized_score']
                      for s in synth_norm if s.get('scope') in ('global', 'entity')}

    # ---- 1. Scores par couche, par période -------------------------------------------
    for pid in PILOT_PERIODS:
        period_has_synthesis = pid in periods_with_synthesis
        rows = []
        for fam in family_order:
            sr = layer_raw.get((pid, fam, 'strategic_reality'))
            if sr is None:
                continue  # famille non scorée pour cette période
            pd = layer_raw.get((pid, fam, 'political_doctrine'))
            ai = layer_raw.get((pid, fam, 'academic_influence'))

            def admitted(entry):
                # couche admise = présente et non deprecated
                return entry is not None and entry[1] != 'deprecated'

            rejected = [l for l, e in (('political_doctrine', pd), ('academic_influence', ai))
                        if e is not None and e[1] == 'deprecated']
            synthesizable = (pid, fam) in synth_raw_by
            rows.append({
                'period_id': pid,
                'theory_family': fam,
                'strategic_reality': num(sr[0]),
                'political_doctrine': num(pd[0]) if admitted(pd) else 'rejete',
                'academic_influence': num(ai[0]) if admitted(ai) else 'rejete',
                'default_synthesis': num(synth_raw_by.get((pid, fam))),
                'normalized_default': num(synth_norm_by.get((pid, fam))),
                'note': anachronism_note(rejected,
                                         emergence[fam]['academic_influence_from'],
                                         period_has_synthesis),
                '_synth_sort': synth_raw_by.get((pid, fam)),
                '_synthesizable': synthesizable,
            })
        # Synthétisables d'abord (par synthèse décroissante), puis rejetées (ordre taxonomie).
        rows.sort(key=lambda r: (
            0 if r['_synthesizable'] else 1,
            -(r['_synth_sort'] or 0) if r['_synthesizable'] else family_index[r['theory_family']],
        ))
        for r in rows:
            r.pop('_synth_sort'); r.pop('_synthesizable')
        write_csv(f'paper/annexe_pilot_scores_{pid}.csv', rows,
                  ['period_id', 'theory_family', 'strategic_reality', 'political_doctrine',
                   'academic_influence', 'default_synthesis', 'normalized_default', 'note'])

    # ---- 2. Sensibilité (synthèse brute par profil + delta_max + statut) -------------
    profile_ids = [p['profile_id'] for p in profiles]
    sens_fields = ['period_id', 'theory_family'] + [f'synthesis_{pid}' for pid in profile_ids] \
        + ['delta_max', 'sensitivity_status']
    sens_rows = []
    for pid in PILOT_PERIODS:
        fams = sorted(
            [fam for fam in family_order if (pid, fam) in sens_by],
            key=lambda fam: -(sens_by[(pid, fam)].get('default_raw') or 0))
        for fam in fams:
            s = sens_by[(pid, fam)]
            row = {'period_id': pid, 'theory_family': fam,
                   'delta_max': num(s['delta_max']),
                   'sensitivity_status': s['sensitivity_status']}
            for prof_id in profile_ids:
                row[f'synthesis_{prof_id}'] = num(s['by_profile'].get(prof_id))
            sens_rows.append(row)
    write_csv('paper/annexe_pilot_sensitivity.csv', sens_rows, sens_fields)

    # ---- 3. Simulation déterministe de second codage ---------------------------------
    sim_rows = []
    for pid in PILOT_PERIODS:
        if pid not in periods_with_synthesis:
            continue  # 1815-1848 : aucune synthèse, exclue
        fams = [fam for fam in family_order if (pid, fam) in synth_raw_by]
        dominant = max(fams, key=lambda fam: synth_raw_by[(pid, fam)])
        for fam in sorted(fams, key=lambda fam: -synth_raw_by[(pid, fam)]):
            primary = synth_raw_by[(pid, fam)]
            delta = 0.0
            if fam == dominant:
                delta -= SIM_DOMINANT_DISCOUNT
            if fam in SIM_RAISE_FAMILIES:
                delta += SIM_PERIPHERAL_RAISE
            if fam == 'realism' and fam != dominant:
                delta -= SIM_REALISM_DISCOUNT
            simulated = round(primary + delta, 2)
            abs_diff = round(abs(simulated - primary), 2)
            sim_rows.append({
                'period_id': pid,
                'theory_family': fam,
                'primary_synthesis_score': num(primary),
                'simulated_second_score': num(simulated),
                'absolute_difference': num(abs_diff),
                'difference_status': difference_status(abs_diff),
            })
    write_csv('paper/annexe_pilot_intercoder_simulation.csv', sim_rows,
              ['period_id', 'theory_family', 'primary_synthesis_score',
               'simulated_second_score', 'absolute_difference', 'difference_status'])

    # ---- 4. Déclinaison par entité (C4) : 1945-1962 ----------------------------------
    # Le score global lisse l'hétérogénéité ; on quantifie la divergence inter-entités sur
    # la période pilote la mieux dotée. Entités = celles que le papier nomme déjà.
    C4_PERIOD = '1945_1962'
    C4_ENTITIES = ['global_system', 'united_states', 'soviet_union', 'decolonizing_world',
                   'western_europe', 'china', 'united_nations']
    # Familles synthétisables de la période (présentes sur les 3 couches au scope global),
    # triées par synthèse globale décroissante.
    c4_families = [fam for fam in family_order
                   if (C4_PERIOD, 'global_system', fam) in synth_raw_ent]
    c4_families.sort(key=lambda fam: -synth_raw_ent[(C4_PERIOD, 'global_system', fam)])
    entity_rows = []
    for eid in C4_ENTITIES:
        label = 'Système global (référence)' if eid == 'global_system' \
            else (entities.get(eid, {}).get('label_fr') or eid)
        for fam in c4_families:
            rs = synth_raw_ent.get((C4_PERIOD, eid, fam))
            if rs is None:
                continue
            entity_rows.append({
                'period_id': C4_PERIOD,
                'entity_id': eid,
                'entity_label_fr': label,
                'theory_family': fam,
                'synthesis_raw': num(rs),
                'normalized_share': num(synth_norm_ent.get((C4_PERIOD, eid, fam))),
            })
    write_csv('paper/annexe_pilot_entities_1945_1962.csv', entity_rows,
              ['period_id', 'entity_id', 'entity_label_fr', 'theory_family',
               'synthesis_raw', 'normalized_share'])

    # ---- 5. Sous-familles de la taxonomie (C3, reporting pur — aucun score) -----------
    subfamily_rows = []
    for fam in taxonomy:
        for sf in fam.get('subfamilies', []):
            subfamily_rows.append({
                'theory_family_id': fam['theory_family_id'],
                'family_label_fr': fam.get('label_fr', ''),
                'subfamily_id': sf['subfamily_id'],
                'subfamily_label_fr': sf.get('label_fr', ''),
            })
    write_csv('paper/annexe_pilot_subfamilies.csv', subfamily_rows,
              ['theory_family_id', 'family_label_fr', 'subfamily_id', 'subfamily_label_fr'])

    # ---- 6. Non-confusion chiffrée réalisme vs géopolitique (C3) ----------------------
    # Écart de score brut par couche/période : montre que la matrice discrimine deux
    # familles sémantiquement proches au lieu de les confondre. Le cas de divergence
    # maximale est marqué (sélection par les données, non choisie à la main).
    GEO = 'geopolitics_imperialism_reason_of_state'
    rg_rows = []
    for pid in PILOT_PERIODS:
        for layer in ('strategic_reality', 'political_doctrine', 'academic_influence'):
            r = layer_raw.get((pid, 'realism', layer))
            g = layer_raw.get((pid, GEO, layer))
            if r is None or g is None or r[1] == 'deprecated' or g[1] == 'deprecated':
                continue
            rg_rows.append({
                'period_id': pid,
                'layer': layer,
                'realism_raw': num(r[0]),
                'geopolitics_raw': num(g[0]),
                'abs_difference': num(round(abs(r[0] - g[0]), 2)),
            })
    if rg_rows:
        peak = max(rg_rows, key=lambda x: float(x['abs_difference']))
        for r in rg_rows:
            r['max_divergence'] = 'yes' if r is peak else ''
    write_csv('paper/annexe_pilot_realism_vs_geopolitics.csv', rg_rows,
              ['period_id', 'layer', 'realism_raw', 'geopolitics_raw',
               'abs_difference', 'max_divergence'])

    print('Paper artifacts generated')


if __name__ == '__main__':
    main()
