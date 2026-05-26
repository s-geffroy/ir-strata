export type ScoreRecord = {
  period_id: string;
  entity_id: string;
  scope: string;
  layer: string;
  theory_family_id: string;
  raw_score: number;
  normalized_score?: number;
};

export type WeightMap = Record<string, number>;

/** Groupes de critères → {nom_critère: valeur 0-100}. Cf. criteria_scores canoniques. */
export type CriteriaScores = Record<string, Record<string, number>>;

/**
 * Dérive le raw_score depuis les criteria_scores via la formule documentée :
 *   raw = Σ_group  poids[group] · moyenne(valeurs du group)
 * Mirroir exact de compute_scores.derive_raw_from_criteria (Python). Utilisé par la
 * console de codage pour calculer le score en direct pendant la saisie des critères.
 * Retourne null si un groupe attendu est absent/vide.
 */
export function deriveRawFromCriteria(
  criteriaScores: CriteriaScores,
  criteriaWeights: WeightMap,
): number | null {
  if (!criteriaScores) return null;
  let weightedSum = 0;
  for (const [groupName, groupWeight] of Object.entries(criteriaWeights)) {
    const groupValues = criteriaScores[groupName];
    if (!groupValues || Object.keys(groupValues).length === 0) return null;
    const values = Object.values(groupValues);
    const groupMean = values.reduce((a, b) => a + b, 0) / values.length;
    weightedSum += groupWeight * groupMean;
  }
  return Math.round(weightedSum * 10000) / 10000;
}

export function normalizeScores(records: ScoreRecord[]): ScoreRecord[] {
  const groups = new Map<string, ScoreRecord[]>();
  for (const r of records) {
    const key = `${r.period_id}::${r.entity_id}::${r.scope}::${r.layer}`;
    groups.set(key, [...(groups.get(key) ?? []), r]);
  }
  const out: ScoreRecord[] = [];
  for (const items of groups.values()) {
    const denom = items.reduce((acc, r) => acc + r.raw_score, 0);
    for (const r of items) {
      out.push({...r, normalized_score: denom > 0 ? (r.raw_score / denom) * 100 : 0});
    }
  }
  return out;
}

export function normalizeWeights(weights: WeightMap): WeightMap {
  const total = Object.values(weights).reduce((a, b) => a + b, 0);
  if (total <= 0) return weights;
  return Object.fromEntries(Object.entries(weights).map(([k, v]) => [k, v / total]));
}
