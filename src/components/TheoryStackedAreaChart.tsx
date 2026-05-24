import React from 'react';
import {Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis} from 'recharts';
import taxonomy from '../data/canonical/theory_taxonomy.json';
import annualData from '../data/generated/annual_interpolated_scores.json';

const theories = (taxonomy as any).theory_families;
const palette = ['#1f2937', '#2563eb', '#b45309', '#7c3aed', '#059669', '#dc2626', '#0f766e'];

function pivotAnnual() {
  const rows = (annualData as any).scores.filter((r: any) => r.entity_id === 'global_system' && r.layer === 'synthesis');
  const byYear: Record<string, any> = {};
  for (const r of rows) {
    byYear[r.year] ??= {year: r.year};
    byYear[r.year][r.theory_family_id] = r.normalized_score;
  }
  return Object.values(byYear).sort((a: any, b: any) => a.year - b.year);
}

export default function TheoryStackedAreaChart() {
  const data = pivotAnnual();
  return (
    <div style={{width: '100%', height: 420}}>
      <ResponsiveContainer>
        <AreaChart data={data} margin={{top: 20, right: 30, left: 0, bottom: 0}}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis tickFormatter={(v) => `${v}%`} />
          <Tooltip formatter={(value: number, name: string) => [`${Number(value).toFixed(2)}%`, theories.find((t: any) => t.theory_family_id === name)?.label_fr ?? name]} />
          {theories.map((t: any, i: number) => (
            <Area key={t.theory_family_id} type="monotone" dataKey={t.theory_family_id} stackId="1" stroke={palette[i % palette.length]} fill={palette[i % palette.length]} fillOpacity={0.75} />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
