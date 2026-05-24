import React from 'react';
import Layout from '@theme/Layout';
import taxonomy from '../../data/canonical/theory_taxonomy.json';

export default function Theories() {
  return <Layout title="Théories"><main className="container margin-vert--lg"><h1>Théories</h1><div className="atlas-grid">{(taxonomy as any).theory_families.map((t: any) => <div className="atlas-card" key={t.theory_family_id}><h3>{t.label_fr}</h3><p><code>{t.theory_family_id}</code></p><p>{t.subfamilies.length} sous-familles activables.</p></div>)}</div></main></Layout>;
}
