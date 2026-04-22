import { describe, expect, it } from "vitest";
import { blendLeaderboards, minMaxNormalize, normalizeWeights } from "./blend";
import type { LeaderboardEntry } from "@/types";

function entry(
  modelId: number,
  name: string,
  score: string,
): LeaderboardEntry {
  return {
    model: {
      id: modelId,
      name,
      provider: { id: 1, name: "p", website: "" },
      is_open_source: false,
    },
    score,
    measured_at: "2026-04-01T00:00:00Z",
  };
}

describe("minMaxNormalize", () => {
  it("scales to [0, 1]", () => {
    expect(minMaxNormalize([0, 5, 10])).toEqual([0, 0.5, 1]);
  });

  it("returns all 1s when every value is identical", () => {
    expect(minMaxNormalize([3, 3, 3])).toEqual([1, 1, 1]);
  });

  it("handles empty input", () => {
    expect(minMaxNormalize([])).toEqual([]);
  });
});

describe("normalizeWeights", () => {
  it("normalizes to sum 1", () => {
    const out = normalizeWeights([1, 2], { 1: 3, 2: 1 });
    expect((out[1] ?? 0) + (out[2] ?? 0)).toBeCloseTo(1);
    expect(out[1]).toBeCloseTo(0.75);
  });

  it("defaults missing weights to 1", () => {
    const out = normalizeWeights([1, 2], {});
    expect(out[1]).toBeCloseTo(0.5);
    expect(out[2]).toBeCloseTo(0.5);
  });

  it("falls back to even weights when all are zero", () => {
    const out = normalizeWeights([1, 2], { 1: 0, 2: 0 });
    expect(out[1]).toBeCloseTo(0.5);
    expect(out[2]).toBeCloseTo(0.5);
  });
});

describe("blendLeaderboards", () => {
  it("ranks by weighted normalized score", () => {
    const boards = [
      {
        benchmarkId: 1,
        entries: [
          entry(10, "A", "0.9"),
          entry(20, "B", "0.5"),
          entry(30, "C", "0.1"),
        ],
      },
      {
        benchmarkId: 2,
        entries: [
          entry(10, "A", "0.2"),
          entry(20, "B", "0.8"),
          entry(30, "C", "0.5"),
        ],
      },
    ];
    const result = blendLeaderboards(boards, { 1: 1, 2: 1 });
    expect(result.map((r) => r.model.id)).toEqual([20, 10, 30]);
  });

  it("flags models missing from some benchmarks", () => {
    const boards = [
      {
        benchmarkId: 1,
        entries: [entry(10, "A", "0.9"), entry(20, "B", "0.5")],
      },
      {
        benchmarkId: 2,
        entries: [entry(10, "A", "0.2")],
      },
    ];
    const result = blendLeaderboards(boards, { 1: 1, 2: 1 });
    const b = result.find((r) => r.model.id === 20)!;
    expect(b.benchmarksMissing).toEqual([2]);
  });

  it("weights shift ranking", () => {
    const boards = [
      {
        benchmarkId: 1,
        entries: [entry(10, "A", "0.9"), entry(20, "B", "0.1")],
      },
      {
        benchmarkId: 2,
        entries: [entry(10, "A", "0.1"), entry(20, "B", "0.9")],
      },
    ];
    const evenWeights = blendLeaderboards(boards, { 1: 1, 2: 1 });
    expect(evenWeights[0]?.blendedScore).toBeCloseTo(
      evenWeights[1]?.blendedScore ?? NaN,
    );

    const favorFirst = blendLeaderboards(boards, { 1: 3, 2: 1 });
    expect(favorFirst[0]?.model.id).toBe(10);
  });
});
