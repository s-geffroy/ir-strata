import React from 'react';
import Layout from '@theme/Layout';
import entities from '../../data/canonical/entities.json';

export default function Entities() {
  return <Layout title="Entités"><main className="container margin-vert--lg"><h1>Entités P1</h1><table><thead><tr><th>Période</th><th>Entité</th><th>Type</th><th>Poids</th><th>Maturité</th></tr></thead><tbody>{(entities as any).entities.map((e: any) => <tr key={`${e.period_id}-${e.entity_id}`}><td>{e.period_id}</td><td>{e.label_fr}</td><td>{e.entity_type}</td><td>{(e.systemic_weight*100).toFixed(1)}%</td><td>{e.maturity_status}</td></tr>)}</tbody></table></main></Layout>;
}
