import React from 'react';
import {
  Area, AreaChart, CartesianGrid, Line, LineChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts';
import taxonomy from '../data/canonical/theory_taxonomy.json';
import annualSynthesis from '../data/generated/annual_interpolated_scores.json';
import annualLayers from '../data/generated/annual_interpolated_layers.json';

const theories = (taxonomy as any).theory_families;
const palette = ['#1f2937', '#2563eb', '#b45309', '#7c3aed', '#059669', '#dc2626', '#0f766e'];
const labelFr = (id: string) => theories.find((t: any) => t.theory_family_id === id)?.label_fr ?? id;

// La synthèse vit dans annual_interpolated_scores ; les trois couches dans annual_interpolated_layers.
const datasetFor = (layer: string) =>
  layer === 'synthesis'
    ? (annualSynthesis as any).scores
    : (annualLayers as any).scores;

function pivotAnnual(layer: string, field: 'normalized_score' | 'raw_score') {
  const rows = datasetFor(layer).filter(
    (r: any) => r.entity_id === 'global_system' && r.layer === layer,
  );
  const byYear: Record<string, any> = {};
  for (const r of rows) {
    byYear[r.year] ??= {year: r.year};
    byYear[r.year][r.theory_family_id] = r[field];
  }
  return Object.values(byYear).sort((a: any, b: any) => a.year - b.year);
}

export default function TheoryAreaChart({
  layer = 'synthesis',
  height = 320,
  valueMode = 'normalized',
}: {
  layer?: string;
  height?: number;
  valueMode?: 'normalized' | 'raw';
}) {
  const isRaw = valueMode === 'raw';
  const data = pivotAnnual(layer, isRaw ? 'raw_score' : 'normalized_score');

  // Brut : intensités indépendantes (0-100) → lignes NON empilées (elles peuvent se chevaucher).
  // Normalisé : parts relatives → aires empilées (somme = 100 % du groupe choisi).
  return (
    <div style={{width: '100%', height}}>
      <ResponsiveContainer>
        {isRaw ? (
          <LineChart data={data} margin={{top: 16, right: 30, left: 0, bottom: 0}}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis domain={[0, 100]} />
            <Tooltip formatter={(v: number, name: string) => [Number(v).toFixed(0), labelFr(name)]} />
            {theories.map((t: any, i: number) => (
              <Line
                key={t.theory_family_id}
                type="monotone"
                dataKey={t.theory_family_id}
                stroke={palette[i % palette.length]}
                dot={false}
                strokeWidth={2}
                connectNulls={false}
              />
            ))}
          </LineChart>
        ) : (
          <AreaChart data={data} margin={{top: 16, right: 30, left: 0, bottom: 0}}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis domain={[0, 100]} allowDataOverflow ticks={[0, 25, 50, 75, 100]} tickFormatter={(v) => `${v}%`} />
            <Tooltip formatter={(v: number, name: string) => [`${Number(v).toFixed(2)}%`, labelFr(name)]} />
            {theories.map((t: any, i: number) => (
              <Area
                key={t.theory_family_id}
                type="monotone"
                dataKey={t.theory_family_id}
                stackId="1"
                stroke={palette[i % palette.length]}
                fill={palette[i % palette.length]}
                fillOpacity={0.75}
              />
            ))}
          </AreaChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}
