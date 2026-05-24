import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import HistoricalLayersView from '../components/HistoricalLayersView';

export default function Home() {
  return (
    <Layout title="Atlas V1" description="Pondération historique des théories des relations internationales">
      <header className="hero--atlas">
        <div className="container">
          <h1>Pondération historique des théories des relations internationales</h1>
          <p>Un atlas analytique de 1815 à 2026 distinguant réalité stratégique, doctrine politique et influence académique.</p>
        </div>
      </header>
      <main className="container margin-vert--lg">
        <div className="atlas-warning">
          ⚠️ Les pourcentages sont des pondérations analytiques estimées à partir de critères, preuves et niveaux de confiance. Ils ne mesurent pas une quantité directement observable.
        </div>
        <div className="atlas-warning">
          🚧 <strong>Données = seed non vérifié.</strong> Les scores, preuves et références fournis sont un jeu de départ généré, <strong>non vérifié et à re-sourcer</strong>. Ils servent à valider la chaîne technique, pas de référence historique. Voir <Link to="/docs/DATA_PROVENANCE">Provenance des données</Link>.
        </div>
        <h2>Évolution globale par couche analytique</h2>
        <HistoricalLayersView />
        <div className="atlas-grid margin-top--lg">
          <div className="atlas-card"><h3>Explorer</h3><p>Visualiser l’évolution, les périodes et les entités.</p><Link className="button button--primary" to="/explorer">Ouvrir</Link></div>
          <div className="atlas-card"><h3>Périodes</h3><p>Lire les fiches historiques générées depuis les données.</p><Link className="button button--secondary" to="/docs/periods/1945-1962">Lire</Link></div>
          <div className="atlas-card"><h3>Méthode</h3><p>Comprendre la taxonomie, le scoring et l’incertitude.</p><Link className="button button--secondary" to="/docs/methodology/SCORING">Voir</Link></div>
          <div className="atlas-card"><h3>Données</h3><p>Télécharger JSON, CSV, schémas et bibliographie.</p><Link className="button button--secondary" to="/data">Télécharger</Link></div>
        </div>
        <h2 className="margin-top--lg">Comment lire les pourcentages ?</h2>
        <p>Un score <strong>normalisé</strong> indique la part relative d’une théorie <em>dans l’ensemble de théories retenu</em>. Comme ces familles se chevauchent et n’épuisent pas le réel, ce pourcentage n’est <strong>pas une part du monde</strong>. Le score <strong>brut</strong> (0-100) conserve l’intensité analytique de chaque théorie, évaluée indépendamment des autres. Les deux doivent être lus ensemble — la bascule « Brut / Normalisé » du graphique permet de passer de l’un à l’autre.</p>
      </main>
    </Layout>
  );
}
