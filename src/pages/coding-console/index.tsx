import React, {useEffect, useMemo, useState} from 'react';
import Layout from '@theme/Layout';
import scoresRaw from '../../data/canonical/scores_raw.json';
import taxonomy from '../../data/canonical/theory_taxonomy.json';
import periodsData from '../../data/canonical/periods.json';
import evidenceData from '../../data/canonical/evidence.json';
import metadata from '../../data/canonical/model_metadata.json';
import {deriveRawFromCriteria, CriteriaScores, WeightMap} from '../../utils/scoring';

// Sous-ensemble protocole : doit rester aligné avec scripts/intercoder_reliability_test.py.
const PROTOCOL_PERIODS = ['1815_1848', '1945_1962', '1991_2001'];
const PROTOCOL_LAYERS = ['strategic_reality', 'political_doctrine', 'academic_influence'];

const LAYER_LABELS: Record<string, string> = {
  strategic_reality: 'Réalité stratégique',
  political_doctrine: 'Doctrine politique',
  academic_influence: 'Influence académique',
};

// Schéma de critères (uniforme dans tout le corpus). [groupe, critère, libellé].
const CRITERIA_SCHEMA: {group: string; key: string; label: string}[] = [
  {group: 'common_criteria', key: 'explanatory_power', label: 'Pouvoir explicatif'},
  {group: 'common_criteria', key: 'historical_centrality', label: 'Centralité historique'},
  {group: 'common_criteria', key: 'evidence_robustness', label: 'Robustesse des preuves'},
  {group: 'theory_specific_criteria', key: 'fit_to_theory_core', label: 'Adéquation au cœur théorique'},
  {group: 'theory_specific_criteria', key: 'discriminating_value', label: 'Valeur discriminante'},
  {group: 'layer_specific_criteria', key: 'layer_fit', label: 'Adéquation à la couche'},
];

const CRITERIA_WEIGHTS = (metadata as any).default_criteria_weights as WeightMap;

const familyLabel = (id: string): string =>
  (taxonomy as any).theory_families.find((t: any) => t.theory_family_id === id)?.label_fr ?? id;
const periodLabel = (id: string): string => {
  const p = (periodsData as any).periods.find((x: any) => x.period_id === id);
  return p ? `${p.start_year}–${p.end_year}` : id;
};

type CoderValues = Record<string, CriteriaScores>;

// Construit le sous-ensemble protocole, SANS exposer le score ni les critères de l'auteur
// (codage à l'aveugle). On ne garde que le contexte : période, couche, famille, preuves.
function buildProtocolScores() {
  const evidenceById: Record<string, any> = {};
  for (const e of (evidenceData as any).evidence) evidenceById[e.evidence_id] = e;
  return (scoresRaw as any).scores
    .filter(
      (s: any) =>
        s.entity_id === 'global_system' &&
        PROTOCOL_PERIODS.includes(s.period_id) &&
        PROTOCOL_LAYERS.includes(s.layer) &&
        s.maturity_status !== 'deprecated',
    )
    .map((s: any) => ({
      score_id: s.score_id,
      period_id: s.period_id,
      layer: s.layer,
      theory_family_id: s.theory_family_id,
      evidence: (s.evidence_basis ?? [])
        .map((eid: string) => evidenceById[eid])
        .filter(Boolean)
        .map((e: any) => ({label: e.label_fr, summary: e.summary_fr})),
    }));
}

function emptyCriteria(): CriteriaScores {
  const out: CriteriaScores = {};
  for (const {group, key} of CRITERIA_SCHEMA) {
    out[group] = out[group] ?? {};
    out[group][key] = 0;
  }
  return out;
}

export default function CodingConsole() {
  const protocolScores = useMemo(buildProtocolScores, []);
  const storageKey = 'ir-strata-coding-console';

  const [coderId, setCoderId] = useState('');
  const [values, setValues] = useState<CoderValues>({});

  // Chargement depuis localStorage (client uniquement, jamais en SSR).
  useEffect(() => {
    if (typeof window === 'undefined') return;
    try {
      const saved = JSON.parse(window.localStorage.getItem(storageKey) || '{}');
      if (saved.coderId) setCoderId(saved.coderId);
      if (saved.values) setValues(saved.values);
    } catch {
      /* ignore */
    }
  }, []);

  const persist = (nextId: string, nextValues: CoderValues) => {
    if (typeof window === 'undefined') return;
    window.localStorage.setItem(storageKey, JSON.stringify({coderId: nextId, values: nextValues}));
  };

  const setCriterion = (scoreId: string, group: string, key: string, raw: string) => {
    const value = Math.max(0, Math.min(100, Number(raw) || 0));
    setValues((prev) => {
      const current = prev[scoreId] ?? emptyCriteria();
      const next: CoderValues = {
        ...prev,
        [scoreId]: {...current, [group]: {...current[group], [key]: value}},
      };
      persist(coderId, next);
      return next;
    });
  };

  const codedCount = Object.keys(values).length;

  const exportJson = () => {
    const payload = {
      schema_version: '1.0.0',
      coder_id: coderId || 'anonyme',
      coded_at: new Date().toISOString().slice(0, 10),
      protocol: 'Codage à l’aveugle du sous-ensemble protocole (console de codage).',
      scores: Object.entries(values).map(([score_id, criteria_scores]) => ({
        score_id,
        criteria_scores,
      })),
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `coder_${coderId || 'anonyme'}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Layout title="Console de codage" description="Re-codage à l'aveugle pour la fiabilité inter-codeurs">
      <main className="container margin-vert--lg">
        <h1>Console de codage à l’aveugle</h1>
        <p>
          Cette console permet à un·e spécialiste de re-coder le sous-ensemble protocole
          <strong> sans voir les scores de l’auteur</strong>, afin de mesurer la fiabilité
          inter-codeurs. Saisissez les critères (0–100) ; le score brut est calculé en direct
          par la formule documentée. À la fin, exportez votre fichier et transmettez-le pour
          dépôt dans <code>src/data/coders/</code>.
        </p>
        <div className="margin-vert--md">
          <label>
            Identifiant codeur (anonyme) :{' '}
            <input
              type="text"
              value={coderId}
              onChange={(e) => {
                setCoderId(e.target.value);
                persist(e.target.value, values);
              }}
              placeholder="ex. codeur_A"
            />
          </label>{' '}
          <span className="badge badge--secondary">
            {codedCount} / {protocolScores.length} scores saisis
          </span>{' '}
          <button className="button button--primary button--sm" onClick={exportJson} disabled={codedCount === 0}>
            Exporter coder_{coderId || 'anonyme'}.json
          </button>
        </div>

        {protocolScores.map((s: any) => {
          const criteria = values[s.score_id] ?? emptyCriteria();
          const derived = deriveRawFromCriteria(criteria, CRITERIA_WEIGHTS);
          const touched = Boolean(values[s.score_id]);
          return (
            <div className="atlas-card margin-vert--sm" key={s.score_id}>
              <h3>
                {familyLabel(s.theory_family_id)} · {LAYER_LABELS[s.layer]} ·{' '}
                {periodLabel(s.period_id)}
              </h3>
              {s.evidence.length > 0 && (
                <details>
                  <summary>Preuves de contexte ({s.evidence.length})</summary>
                  <ul>
                    {s.evidence.map((e: any, i: number) => (
                      <li key={i}>
                        <strong>{e.label}</strong> — {e.summary}
                      </li>
                    ))}
                  </ul>
                </details>
              )}
              <div className="atlas-grid">
                {CRITERIA_SCHEMA.map(({group, key, label}) => (
                  <label key={key} style={{display: 'block'}}>
                    {label}
                    <br />
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={criteria[group]?.[key] ?? 0}
                      onChange={(e) => setCriterion(s.score_id, group, key, e.target.value)}
                    />
                  </label>
                ))}
              </div>
              <p>
                Score brut dérivé :{' '}
                <strong>{touched && derived !== null ? derived.toFixed(2) : '—'}</strong>
              </p>
            </div>
          );
        })}
      </main>
    </Layout>
  );
}
