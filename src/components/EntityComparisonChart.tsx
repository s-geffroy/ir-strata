import React from 'react';
import {Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis} from 'recharts';
import scoresData from '../data/generated/scores_synthesis_normalized.json';
import entitiesData from '../data/canonical/entities.json';

export default function EntityComparisonChart({periodId, theoryFamily = 'realism'}: {periodId: string; theoryFamily?: string}) {
  const entityLabels = Object.fromEntries((entitiesData as any).entities.map((e: any) => [e.entity_id, e.label_fr]));
  const data = (scoresData as any).scores
    .filter((s: any) => s.period_id === periodId && s.layer === 'synthesis' && s.theory_family_id === theoryFamily && s.entity_id !== 'global_system')
    .map((s: any) => ({entity: entityLabels[s.entity_id] ?? s.entity_id, score: s.normalized_score}))
    .sort((a: any, b: any) => b.score - a.score)
    .slice(0, 12);

  if (!data.length) return <p>Aucun profil d’entité détaillé pour cette période.</p>;

  return <div style={{width: '100%', height: 380}}><ResponsiveContainer><BarChart data={data}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="entity" angle={-30} textAnchor="end" height={100}/><YAxis/><Tooltip formatter={(v: number) => `${Number(v).toFixed(2)}%`}/><Bar dataKey="score" fill="#2f4f4f"/></BarChart></ResponsiveContainer></div>;
}
