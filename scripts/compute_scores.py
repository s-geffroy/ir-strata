#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))

def dump(path, obj):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def derive_raw_from_criteria(criteria_scores, criteria_weights):
    """Dérive le raw_score depuis les criteria_scores via la formule documentée.

    raw = Σ_group  poids[group] · moyenne(valeurs du group)

    `criteria_scores` est un objet à trois groupes (common_criteria,
    theory_specific_criteria, layer_specific_criteria), chacun étant un dict
    {nom_critère: valeur 0-100}. `criteria_weights` mappe chaque group sur son
    poids (cf. model_metadata.json:default_criteria_weights, somme = 1.0).
    Retourne None si les critères sont absents/incomplets (ex. scores générés).
    """
    if not criteria_scores:
        return None
    weighted_sum = 0.0
    for group_name, group_weight in criteria_weights.items():
        group_values = criteria_scores.get(group_name)
        if not group_values:
            return None
        group_mean = sum(float(v) for v in group_values.values()) / len(group_values)
        weighted_sum += group_weight * group_mean
    return round(weighted_sum, 4)


def sensitivity_status(delta_max):
    """Statut de sensibilité d'un score synthétique à la pondération des couches,
    selon l'écart brut maximal (delta_max) entre profils, d'après le codebook :
    robuste (<=5), modérément sensible (6-10), sensible (11-15), très sensible (>15)."""
    if delta_max <= 5:
        return 'robuste'
    if delta_max <= 10:
        return 'moderement_sensible'
    if delta_max <= 15:
        return 'sensible'
    return 'tres_sensible'


def normalize(records):
    groups = {}
    for s in records:
        if s.get('maturity_status') == 'deprecated':
            continue
        key = (s['period_id'], s['entity_id'], s['scope'], s['layer'])
        groups.setdefault(key, []).append(s)
    out=[]
    for key, items in groups.items():
        denom = sum(float(x['raw_score']) for x in items)
        if denom <= 0:
            continue
        for x in items:
            out.append({
                'score_id': x['score_id'],
                'period_id': x['period_id'],
                'entity_id': x['entity_id'],
                'scope': x['scope'],
                'layer': x['layer'],
                'theory_family_id': x['theory_family_id'],
                'raw_score': x['raw_score'],
                'normalized_score': round((x['raw_score'] / denom) * 100, 4),
                'confidence': x.get('confidence'),
                'maturity_status': x.get('maturity_status'),
                'derivation_status': 'generated_normalized_from_raw'
            })
    return out

def synthesize(records, weights):
    groups={}
    for s in records:
        if s.get('maturity_status') == 'deprecated':
            continue
        if s['layer'] not in weights:
            continue
        key=(s['period_id'], s['entity_id'], s['scope'], s['theory_family_id'])
        groups.setdefault(key,{})[s['layer']]=s
    out=[]
    for (pid,eid,scope,tid), layers in groups.items():
        if not all(k in layers for k in weights):
            continue
        raw = sum(layers[k]['raw_score'] * w for k,w in weights.items())
        out.append({
            'score_id': f'score_{pid}_{eid}_synthesis_{tid}',
            'period_id': pid,
            'entity_id': eid,
            'scope': scope,
            'layer': 'synthesis',
            'theory_family_id': tid,
            'raw_score': round(raw, 2),
            'confidence': layers.get('strategic_reality', next(iter(layers.values()))).get('confidence'),
            'maturity_status': 'generated',
            'derivation_status': 'generated_synthesis_from_layer_scores'
        })
    return out

def main():
    metadata = load('src/data/canonical/model_metadata.json')
    raw = load('src/data/canonical/scores_raw.json')['scores'] + load('src/data/canonical/scores_entities_raw.json')['scores']
    normalized = normalize(raw)
    synthesis = synthesize(raw, metadata['default_synthesis_weights'])
    synthesis_norm = normalize(synthesis)

    dump('src/data/generated/scores_normalized.json', {'schema_version':'1.0.0','scores': normalized})
    dump('src/data/generated/scores_synthesis_raw.json', {'schema_version':'1.0.0','scores': synthesis})
    dump('src/data/generated/scores_synthesis_normalized.json', {'schema_version':'1.0.0','scores': synthesis_norm})

    # Annual constant projection for global synthesis only
    periods = {p['period_id']: p for p in load('src/data/canonical/periods.json')['periods']}
    annual=[]
    for s in synthesis_norm:
        if s['entity_id'] != 'global_system':
            continue
        p = periods[s['period_id']]
        for year in range(p['start_year'], p['end_year'] + 1):
            annual.append({
                'year': year,
                'period_id': s['period_id'],
                'entity_id': s['entity_id'],
                'scope': s['scope'],
                'layer': 'synthesis',
                'theory_family_id': s['theory_family_id'],
                'raw_score': s['raw_score'],
                'normalized_score': s['normalized_score'],
                'confidence_label': s['confidence']['label'] if s.get('confidence') else '',
                'derivation_status': 'derived_constant',
                'source_score_id': s['score_id']
            })

    dump('src/data/generated/annual_interpolated_scores.json', {'schema_version':'1.0.0','scores': annual})

    # Annual constant projection PER LAYER (global_system only).
    # Permet de découpler l'affichage : montrer les trois couches séparément dans le temps,
    # au lieu d'imposer la seule synthèse pondérée.
    LAYER_KEYS = ('strategic_reality', 'political_doctrine', 'academic_influence')
    annual_layers = []
    for s in normalized:
        if s['entity_id'] != 'global_system' or s['layer'] not in LAYER_KEYS:
            continue
        p = periods[s['period_id']]
        for year in range(p['start_year'], p['end_year'] + 1):
            annual_layers.append({
                'year': year,
                'period_id': s['period_id'],
                'entity_id': s['entity_id'],
                'scope': s['scope'],
                'layer': s['layer'],
                'theory_family_id': s['theory_family_id'],
                'raw_score': s['raw_score'],
                'normalized_score': s['normalized_score'],
                'confidence_label': s['confidence']['label'] if s.get('confidence') else '',
                'derivation_status': 'derived_constant',
                'source_score_id': s['score_id'],
            })
    dump('src/data/generated/annual_interpolated_layers.json',
         {'schema_version': '1.0.0', 'scores': annual_layers})

    # Sensibilité de la synthèse à la pondération = incertitude de l'agrégation.
    # Pour global_system, on recalcule la synthèse normalisée sous CHAQUE profil de poids
    # et on expose min/max/écart : le chiffre agrégé n'est pas une vérité unique.
    profiles = load('src/data/canonical/weight_profiles.json')['profiles']
    by_profile = {}  # (period_id, theory_family_id) -> {profile_id: normalized_score}
    for prof in profiles:
        prof_norm = normalize(synthesize(raw, prof['weights']))
        for s in prof_norm:
            if s['entity_id'] != 'global_system':
                continue
            by_profile.setdefault((s['period_id'], s['theory_family_id']), {})[prof['profile_id']] = s['normalized_score']

    sensitivity = []
    for (pid, tid), per_prof in by_profile.items():
        values = list(per_prof.values())
        sensitivity.append({
            'period_id': pid,
            'entity_id': 'global_system',
            'scope': 'global',
            'theory_family_id': tid,
            'default_normalized': per_prof.get('default'),
            'min_normalized': round(min(values), 4),
            'max_normalized': round(max(values), 4),
            'spread': round(max(values) - min(values), 4),
            'by_profile': {k: round(v, 4) for k, v in per_prof.items()},
        })
    dump('src/data/generated/scores_synthesis_sensitivity.json',
         {'schema_version': '1.0.0', 'weights_source': 'weight_profiles.json', 'scores': sensitivity})

    # Sensibilité de la synthèse BRUTE à la pondération.
    # Le fichier ci-dessus mesure le déplacement de la PART normalisée ; celui-ci mesure
    # le déplacement du score brut synthétique (prioritaire dans la méthode) sous chaque
    # profil. Le delta_max (écart brut max-min entre profils) est interprété via les
    # seuils du codebook : robuste / modérément sensible / sensible / très sensible.
    raw_by_profile = {}  # (period_id, theory_family_id) -> {profile_id: raw_synthesis}
    for prof in profiles:
        for s in synthesize(raw, prof['weights']):
            if s['entity_id'] != 'global_system':
                continue
            raw_by_profile.setdefault((s['period_id'], s['theory_family_id']), {})[prof['profile_id']] = s['raw_score']

    sensitivity_raw = []
    for (pid, tid), per_prof in raw_by_profile.items():
        values = list(per_prof.values())
        delta_max = round(max(values) - min(values), 4)
        sensitivity_raw.append({
            'period_id': pid,
            'entity_id': 'global_system',
            'scope': 'global',
            'theory_family_id': tid,
            'default_raw': per_prof.get('default'),
            'min_raw': round(min(values), 4),
            'max_raw': round(max(values), 4),
            'delta_max': delta_max,
            'sensitivity_status': sensitivity_status(delta_max),
            'by_profile': {k: round(v, 4) for k, v in per_prof.items()},
        })
    dump('src/data/generated/scores_synthesis_sensitivity_raw.json',
         {'schema_version': '1.0.0', 'weights_source': 'weight_profiles.json',
          'status_thresholds': {'robuste': '<=5', 'moderement_sensible': '6-10',
                                'sensible': '11-15', 'tres_sensible': '>15'},
          'scores': sensitivity_raw})

    # Dérivation transparente raw_score ⟵ criteria_scores.
    # Rend visible l'écart entre le score saisi à la main (raw_authored) et celui que
    # produit la formule appliquée à ses propres critères (raw_derived). validate_model.py
    # transforme cet écart en gate bloquant ; ici on l'expose simplement pour audit.
    criteria_weights = metadata['default_criteria_weights']
    derived = []
    for s in raw:
        if s.get('maturity_status') == 'deprecated':
            continue
        raw_derived = derive_raw_from_criteria(s.get('criteria_scores'), criteria_weights)
        if raw_derived is None:
            continue
        raw_authored = float(s['raw_score'])
        derived.append({
            'score_id': s['score_id'],
            'period_id': s['period_id'],
            'entity_id': s['entity_id'],
            'scope': s['scope'],
            'layer': s['layer'],
            'theory_family_id': s['theory_family_id'],
            'raw_authored': raw_authored,
            'raw_derived': raw_derived,
            'delta': round(raw_authored - raw_derived, 4),
            'derivation_status': 'generated_raw_from_criteria',
        })
    dump('src/data/generated/scores_derived_from_criteria.json',
         {'schema_version': '1.0.0', 'criteria_weights': criteria_weights, 'scores': derived})

    print('Scores generated')


if __name__ == '__main__':
    main()
