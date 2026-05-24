import React from 'react';
import Layout from '@theme/Layout';

export default function DataPage() {
  const files = [
    ['Modèle complet JSON', '/exports/ir_theory_model_full.json'],
    ['Scores globaux CSV', '/exports/scores_global.csv'],
    ['Scores entités CSV', '/exports/scores_entities.csv'],
    ['Scores annuels interpolés CSV', '/exports/annual_interpolated_scores.csv'],
  ];
  return <Layout title="Données"><main className="container margin-vert--lg"><h1>Données</h1><p>Les exports publics sont générés depuis les JSON canoniques.</p><ul>{files.map(([label, href]) => <li key={href}><a href={href}>{label}</a></li>)}</ul></main></Layout>;
}
