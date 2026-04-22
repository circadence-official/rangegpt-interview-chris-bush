import type { LeaderboardEntry, LeaderboardModel } from "@/types";

export interface NormalizedScore {
  benchmarkId: number;
  score: number;
  normalized: number;
}

export interface BlendedRow {
  model: LeaderboardModel;
  blendedScore: number;
  perBenchmark: Map<number, NormalizedScore>;
  benchmarksMissing: number[];
}

export function minMaxNormalize(values: number[]): number[] {
  if (values.length === 0) return [];
  const min = Math.min(...values);
  const max = Math.max(...values);
  if (max === min) {
    return values.map(() => 1);
  }
  return values.map((v) => (v - min) / (max - min));
}

export function normalizeWeights(
  benchmarkIds: number[],
  weights: Record<number, number>,
): Record<number, number> {
  const raw = benchmarkIds.map((id) => Math.max(0, weights[id] ?? 1));
  const sum = raw.reduce((a, b) => a + b, 0);
  if (sum === 0 || benchmarkIds.length === 0) {
    const even = benchmarkIds.length === 0 ? 0 : 1 / benchmarkIds.length;
    return Object.fromEntries(benchmarkIds.map((id) => [id, even]));
  }
  return Object.fromEntries(
    benchmarkIds.map((id, i) => [id, (raw[i] ?? 0) / sum]),
  );
}

export function blendLeaderboards(
  leaderboards: { benchmarkId: number; entries: LeaderboardEntry[] }[],
  rawWeights: Record<number, number>,
): BlendedRow[] {
  if (leaderboards.length === 0) return [];

  const benchmarkIds = leaderboards.map((l) => l.benchmarkId);
  const weights = normalizeWeights(benchmarkIds, rawWeights);

  const normalizedByBenchmark = new Map<number, Map<number, NormalizedScore>>();
  for (const { benchmarkId, entries } of leaderboards) {
    const scores = entries.map((e) => parseFloat(e.score));
    const normalized = minMaxNormalize(scores);
    const perModel = new Map<number, NormalizedScore>();
    entries.forEach((entry, i) => {
      perModel.set(entry.model.id, {
        benchmarkId,
        score: scores[i] ?? 0,
        normalized: normalized[i] ?? 0,
      });
    });
    normalizedByBenchmark.set(benchmarkId, perModel);
  }

  const modelsById = new Map<number, LeaderboardModel>();
  for (const { entries } of leaderboards) {
    for (const entry of entries) {
      if (!modelsById.has(entry.model.id)) {
        modelsById.set(entry.model.id, entry.model);
      }
    }
  }

  const rows: BlendedRow[] = [];
  for (const [modelId, model] of modelsById) {
    let blended = 0;
    const perBenchmark = new Map<number, NormalizedScore>();
    const missing: number[] = [];
    for (const benchmarkId of benchmarkIds) {
      const score = normalizedByBenchmark.get(benchmarkId)?.get(modelId);
      if (score) {
        perBenchmark.set(benchmarkId, score);
        blended += (weights[benchmarkId] ?? 0) * score.normalized;
      } else {
        missing.push(benchmarkId);
      }
    }
    rows.push({
      model,
      blendedScore: blended,
      perBenchmark,
      benchmarksMissing: missing,
    });
  }

  rows.sort((a, b) => b.blendedScore - a.blendedScore);
  return rows;
}
