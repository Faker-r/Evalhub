export type ModelProviderKey = string;

export function toModelProviderKey(model: string, provider: string): ModelProviderKey {
  return `${provider}::${model}`;
}

export interface ModelScoreCell {
  score: number | Record<string, unknown>;
  trace_id: number;
  created_at: string;
  spec: Record<string, unknown> | null;
}

export interface ComparisonRow {
  dataset: string;
  metric: string;
  models: Record<ModelProviderKey, ModelScoreCell>;
}

export type SideBySideApiEntry = {
  model: string;
  provider: string;
  dataset_name: string;
  metric_name: string;
  trace_id: number;
  created_at: string;
  score?: number | Record<string, unknown>;
};

export type SpecByTrace = Record<string, Record<string, unknown> | null>;

export function buildComparisonRows(
  entries: SideBySideApiEntry[],
  specByTrace: SpecByTrace
): ComparisonRow[] {
  const byKey = new Map<string, Map<ModelProviderKey, ModelScoreCell>>();
  for (const e of entries) {
    const rowKey = `${e.dataset_name}\t${e.metric_name}`;
    if (!byKey.has(rowKey)) {
      byKey.set(rowKey, new Map<ModelProviderKey, ModelScoreCell>());
    }
    const rowMap = byKey.get(rowKey)!;
    const modelKey = toModelProviderKey(e.model, e.provider);
    const existing = rowMap.get(modelKey);
    const createdMs = new Date(e.created_at).getTime();
    const existingMs = existing ? new Date(existing.created_at).getTime() : 0;
    if (!existing || createdMs > existingMs) {
      const spec = specByTrace[String(e.trace_id)] ?? null;
      rowMap.set(modelKey, {
        score: e.score ?? 0,
        trace_id: e.trace_id,
        created_at: e.created_at,
        spec,
      });
    }
  }
  const rows: ComparisonRow[] = [];
  for (const [rowKey, modelMap] of byKey) {
    const [dataset, metric] = rowKey.split('\t');
    const models: Record<ModelProviderKey, ModelScoreCell> = {};
    modelMap.forEach((v, k) => {
      models[k] = v;
    });
    rows.push({ dataset, metric, models });
  }
  return rows;
}

function extractNumericScore(score: number | Record<string, unknown>): number | null {
  if (typeof score === 'number' && !Number.isNaN(score)) return score;
  if (score && typeof score === 'object' && 'mean' in score && typeof (score as { mean: unknown }).mean === 'number') {
    return (score as { mean: number }).mean;
  }
  if (score && typeof score === 'object' && 'value' in score && typeof (score as { value: unknown }).value === 'number') {
    return (score as { value: number }).value;
  }
  return null;
}

const CAPABILITY_ORDER = ['Reasoning', 'Coding', 'Math', 'Creativity', 'Instruction', 'Factuality'] as const;

const DATASET_TO_CAPABILITY: Record<string, (typeof CAPABILITY_ORDER)[number]> = {
  gsm8k: 'Reasoning',
  mmlu: 'Reasoning',
  humaneval: 'Coding',
  math: 'Math',
  ifeval: 'Instruction',
  truthfulqa: 'Factuality',
};

function capabilityForDataset(datasetName: string): (typeof CAPABILITY_ORDER)[number] | null {
  const lower = datasetName.toLowerCase();
  for (const [key, cap] of Object.entries(DATASET_TO_CAPABILITY)) {
    if (lower.includes(key)) return cap;
  }
  if (lower.includes('creative')) return 'Creativity';
  return null;
}

export interface RadarPoint {
  subject: (typeof CAPABILITY_ORDER)[number];
  fullMark: number;
  [modelKey: string]: string | number;
}

export function buildRadarData(
  rows: ComparisonRow[],
  modelKeys: ModelProviderKey[],
  scaleMax = 100
): RadarPoint[] {
  type Bucket = { sum: number; count: number; byModel: Record<string, { sum: number; count: number }> };
  const byCapability: Record<string, Bucket> = {};
  for (const cap of CAPABILITY_ORDER) {
    byCapability[cap] = { sum: 0, count: 0, byModel: {} };
    for (const mk of modelKeys) {
      byCapability[cap].byModel[mk] = { sum: 0, count: 0 };
    }
  }
  for (const row of rows) {
    const cap = capabilityForDataset(row.dataset);
    if (!cap) continue;
    const bucket = byCapability[cap];
    for (const mk of modelKeys) {
      const cell = row.models[mk];
      if (!cell) continue;
      const num = extractNumericScore(cell.score);
      if (num == null) continue;
      let normalized = num;
      if (num <= 1 && scaleMax === 100) normalized = num * 100;
      else if (num > 100 && scaleMax === 100) normalized = Math.min(100, num);
      bucket.byModel[mk].sum += normalized;
      bucket.byModel[mk].count += 1;
    }
  }
  return CAPABILITY_ORDER.map((subject) => {
    const bucket = byCapability[subject];
    const point: RadarPoint = { subject, fullMark: scaleMax };
    for (const mk of modelKeys) {
      const b = bucket.byModel[mk];
      point[mk] = b.count > 0 ? Math.round((b.sum / b.count) * 10) / 10 : 0;
    }
    return point;
  });
}

export function getDisplayScore(score: number | Record<string, unknown>): { type: 'number'; value: string } | { type: 'object' } {
  const num = extractNumericScore(score);
  if (num != null) return { type: 'number', value: num.toFixed(2) };
  return { type: 'object' };
}

export function getDisplayStd(score: number | Record<string, unknown>): string | null {
  if (!score || typeof score !== 'object' || !('std' in score)) return null;
  const s = (score as { std: unknown }).std;
  if (typeof s !== 'number' || Number.isNaN(s) || s === 0) return null;
  return s.toFixed(2);
}

export function getNumericForDiff(score: number | Record<string, unknown>): number | null {
  return extractNumericScore(score);
}

// New interface for grouped bar chart data
export interface BarChartDataPoint {
  benchmark: string;
  metric: string;
  modelScores: Record<ModelProviderKey, number | null>;
}

export function buildGroupedBarData(
  rows: ComparisonRow[],
  modelKeys: ModelProviderKey[]
): BarChartDataPoint[] {
  return rows.map((row) => {
    const modelScores: Record<ModelProviderKey, number | null> = {};

    for (const mk of modelKeys) {
      const cell = row.models[mk];
      if (cell) {
        const num = extractNumericScore(cell.score);
        modelScores[mk] = num != null ? num : null;
      } else {
        modelScores[mk] = null;
      }
    }

    return {
      benchmark: row.dataset,
      metric: row.metric,
      modelScores,
    };
  }).filter((point) => {
    // Only include benchmarks where at least one model has a valid score
    return Object.values(point.modelScores).some((score) => score !== null);
  });
}
