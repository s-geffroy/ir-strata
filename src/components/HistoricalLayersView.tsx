import React, {useState} from 'react';
import TheoryAreaChart from './TheoryAreaChart';

// Vue historique globale DÉCOUPLÉE :
//  - couche : les trois couches séparées (par défaut) ou la synthèse pondérée (dérivée) ;
//  - échelle : normalisé (part relative, empilé) ou brut (intensité indépendante, lignes).
// Le mode brut, non empilé, rappelle que les familles ne sont ni exclusives ni exhaustives :
// les pourcentages normalisés sont des parts relatives dans un ensemble choisi, pas des
// parts du réel.

const LAYERS = [
  {id: 'strategic_reality', label: 'Réalité stratégique'},
  {id: 'political_doctrine', label: 'Doctrine politique'},
  {id: 'academic_influence', label: 'Influence académique'},
];

type Mode = 'layers' | 'synthesis';
type Scale = 'normalized' | 'raw';

export default function HistoricalLayersView() {
  const [mode, setMode] = useState<Mode>('layers');
  const [scale, setScale] = useState<Scale>('normalized');

  const btn = (active: boolean): React.CSSProperties => ({
    padding: '0.4rem 0.9rem',
    marginRight: '0.5rem',
    cursor: 'pointer',
    border: '1px solid var(--ifm-color-emphasis-300)',
    borderRadius: 6,
    background: active ? 'var(--ifm-color-primary)' : 'transparent',
    color: active ? 'white' : 'inherit',
    fontWeight: active ? 600 : 400,
  });

  return (
    <div>
      <div role="tablist" aria-label="Couche" style={{marginBottom: '0.5rem'}}>
        <button role="tab" aria-selected={mode === 'layers'} style={btn(mode === 'layers')}
          onClick={() => setMode('layers')}>Trois couches (séparées)</button>
        <button role="tab" aria-selected={mode === 'synthesis'} style={btn(mode === 'synthesis')}
          onClick={() => setMode('synthesis')}>Synthèse pondérée (dérivée)</button>
      </div>
      <div role="tablist" aria-label="Échelle" style={{marginBottom: '1rem'}}>
        <button role="tab" aria-selected={scale === 'normalized'} style={btn(scale === 'normalized')}
          onClick={() => setScale('normalized')}>Normalisé (part relative)</button>
        <button role="tab" aria-selected={scale === 'raw'} style={btn(scale === 'raw')}
          onClick={() => setScale('raw')}>Brut (intensité analytique)</button>
      </div>

      {scale === 'normalized' ? (
        <div className="atlas-warning">
          ↔️ <strong>Lecture des parts normalisées.</strong> Les familles théoriques{' '}
          <strong>se chevauchent et n'épuisent pas le réel</strong> : un « 30 % réalisme »
          est une part relative <em>dans l'ensemble choisi de théories</em>, pas une part du
          monde. Pour des intensités indépendantes, basculez en vue <em>Brut</em>.
        </div>
      ) : (
        <div className="atlas-warning">
          📏 <strong>Vue brute.</strong> Chaque ligne est l'intensité analytique (0-100) d'une
          théorie, évaluée <strong>indépendamment</strong> des autres : les lignes peuvent se
          chevaucher et ne somment pas à 100 %.
        </div>
      )}

      {mode === 'layers' ? (
        <div>
          {LAYERS.map((l) => (
            <section key={l.id} style={{marginBottom: '1.5rem'}}>
              <h3 style={{marginBottom: '0.25rem'}}>{l.label}</h3>
              <TheoryAreaChart layer={l.id} height={260} valueMode={scale} />
            </section>
          ))}
          <p>
            <em>
              Les trois couches mesurent des dimensions différentes — réalité stratégique
              (lecture rétrospective), doctrine politique assumée à l'époque, influence
              académique — et ne sont pas directement commensurables. Elles sont présentées
              séparément par défaut.
            </em>
          </p>
        </div>
      ) : (
        <div>
          <div className="atlas-warning">
            ⚖️ La synthèse agrège ces trois dimensions via une <strong>pondération
            conventionnelle</strong> (par défaut 60 / 25 / 15). Le chiffre obtenu{' '}
            <strong>dépend de ce choix</strong> et ne doit pas être lu comme une vérité unique.
            Elle n'est calculée que là où les trois couches existent légitimement (cf.
            anti-anachronisme).
          </div>
          <TheoryAreaChart layer="synthesis" height={360} valueMode={scale} />
        </div>
      )}
    </div>
  );
}
