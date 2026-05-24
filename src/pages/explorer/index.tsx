import React from 'react';
import Layout from '@theme/Layout';
import HistoricalLayersView from '../../components/HistoricalLayersView';
import WeightControlPanel from '../../components/WeightControlPanel';
import PeriodScoreTable from '../../components/PeriodScoreTable';
import EntityComparisonChart from '../../components/EntityComparisonChart';

export default function Explorer() {
  return (
    <Layout title="Explorer">
      <main className="container margin-vert--lg">
        <h1>Explorer</h1>
        <div className="atlas-warning">Les données V1 incluent des objets `draft`. Vérifier la maturité avant conclusion.</div>
        <WeightControlPanel />
        <h2>Vue historique globale</h2>
        <HistoricalLayersView />
        <h2>Exemple de fiche-score : 1991-2001</h2>
        <PeriodScoreTable periodId="1991_2001" />
        <h2>Comparaison d’entités : réalisme, 2022-2026</h2>
        <EntityComparisonChart periodId="2022_2026" theoryFamily="realism" />
      </main>
    </Layout>
  );
}
