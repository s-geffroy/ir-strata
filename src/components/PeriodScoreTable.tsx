import React from 'react';
import ConfidenceBadge from './ConfidenceBadge';
import taxonomy from '../data/canonical/theory_taxonomy.json';
import layerData from '../data/generated/scores_normalized.json';
import synthData from '../data/generated/scores_synthesis_normalized.json';
import sensData from '../data/generated/scores_synthesis_sensitivity.json';

const labels = Object.fromEntries(
  (taxonomy as any).theory_families.map((t: any) => [t.theory_family_id, t.label_fr]),
);

const LAYER_KEYS = ['strategic_reality', 'political_doctrine', 'academic_influence'] as const;

// Fiche-score DÉCOUPLÉE : les trois couches sont affichées séparément (colonnes distinctes),
// et la synthèse est accompagnée de sa plage de variation selon le profil de pondération,
// pour ne pas imposer le chiffre agrégé comme une vérité unique.
export default function PeriodScoreTable({
  periodId,
  entityId = 'global_system',
}: {
  periodId: string;
  entityId?: string;
}) {
  const inScope = (s: any) => s.period_id === periodId && s.entity_id === entityId;
  const layerRows = (layerData as any).scores.filter(inScope);
  const synthRows = (synthData as any).scores.filter(
    (s: any) => inScope(s) && s.layer === 'synthesis',
  );
  const sensByTheory: Record<string, any> = Object.fromEntries(
    (sensData as any).scores.filter(inScope).map((s: any) => [s.theory_family_id, s]),
  );

  if (!synthRows.length && !layerRows.length) return <p>Aucun score disponible.</p>;

  const byTheory: Record<string, any> = {};
  for (const s of layerRows) {
    byTheory[s.theory_family_id] ??= {layers: {}};
    byTheory[s.theory_family_id].layers[s.layer] = s;
  }
  for (const s of synthRows) {
    byTheory[s.theory_family_id] ??= {layers: {}};
    byTheory[s.theory_family_id].synth = s;
  }

  const rows = Object.entries(byTheory).sort(
    (a: any, b: any) => (b[1].synth?.normalized_score ?? 0) - (a[1].synth?.normalized_score ?? 0),
  );

  // Chaque cellule de couche montre la part normalisée ET le score brut, pour ne pas
  // réduire la lecture à la seule part relative (qui suppose à tort des familles exhaustives).
  const cell = (rec: any) =>
    rec ? (
      <>
        {rec.normalized_score.toFixed(1)}%
        <br />
        <small style={{opacity: 0.7}}>brut {rec.raw_score}</small>
      </>
    ) : (
      '—'
    );

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Théorie</th>
            <th>Réalité stratégique</th>
            <th>Doctrine politique</th>
            <th>Influence académique</th>
            <th>Synthèse (défaut)</th>
            <th>Plage selon pondération</th>
            <th>Confiance</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(([tid, rec]: any) => {
            const sens = sensByTheory[tid];
            const conf = rec.synth?.confidence ?? rec.layers?.strategic_reality?.confidence;
            return (
              <tr key={tid}>
                <td>{labels[tid] ?? tid}</td>
                {LAYER_KEYS.map((k) => (
                  <td key={k}>{cell(rec.layers?.[k])}</td>
                ))}
                <td>{rec.synth ? `${rec.synth.normalized_score.toFixed(1)}%` : '—'}</td>
                <td>
                  {sens
                    ? `${sens.min_normalized.toFixed(1)}–${sens.max_normalized.toFixed(1)}% (±${(sens.spread / 2).toFixed(1)})`
                    : '—'}
                </td>
                <td><ConfidenceBadge label={conf?.label} /></td>
              </tr>
            );
          })}
        </tbody>
      </table>
      <p>
        <em>
          Chaque cellule indique la part normalisée et le score brut (intensité analytique
          indépendante, 0-100). Les trois couches sont normalisées séparément (chacune somme à
          100 % sur la période) ; comme les familles ne sont ni exclusives ni exhaustives, ces
          parts sont relatives à l'ensemble des théories retenu, non au monde. La colonne
          « Synthèse » applique la pondération par défaut (60 / 25 / 15) ; la « Plage » montre
          l'écart obtenu en variant le profil — plus elle est large, moins le chiffre agrégé est
          robuste.
        </em>
      </p>
    </div>
  );
}
