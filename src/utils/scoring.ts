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
