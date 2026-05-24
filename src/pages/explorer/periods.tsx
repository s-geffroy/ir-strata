import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import periodsData from '../../data/canonical/periods.json';

export default function Periods() {
  return <Layout title="Périodes"><main className="container margin-vert--lg"><h1>Périodes</h1><ul>{(periodsData as any).periods.map((p: any) => <li key={p.period_id}><Link to={`/docs/periods/${p.label}`}>{p.label} — {p.title_fr}</Link> <code>{p.priority}</code></li>)}</ul></main></Layout>;
}
