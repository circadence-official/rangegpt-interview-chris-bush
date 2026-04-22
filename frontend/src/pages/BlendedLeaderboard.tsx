import { useMemo, useState } from "react";
import { Link } from "react-router";
import { useBenchmarks } from "@/hooks/useBenchmarks";
import { useLeaderboards } from "@/hooks/useLeaderboard";
import { blendLeaderboards } from "@/lib/blend";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

export default function BlendedLeaderboard() {
  const { data: benchmarks, isLoading: loadingBenchmarks } = useBenchmarks();
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [weights, setWeights] = useState<Record<number, number>>({});

  const allIds = useMemo(() => benchmarks?.map((b) => b.id) ?? [], [benchmarks]);
  const activeIds = selectedIds.length > 0 ? selectedIds : allIds;

  const leaderboardQueries = useLeaderboards(activeIds);

  const blended = useMemo(() => {
    if (leaderboardQueries.some((q) => q.isLoading || !q.data)) return null;
    const boards = activeIds.map((id, i) => ({
      benchmarkId: id,
      entries: leaderboardQueries[i]?.data ?? [],
    }));
    return blendLeaderboards(boards, weights);
  }, [leaderboardQueries, activeIds, weights]);

  function toggleBenchmark(id: number) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((b) => b !== id) : [...prev, id],
    );
  }

  function updateWeight(id: number, value: number) {
    setWeights((prev) => ({ ...prev, [id]: value }));
  }

  if (loadingBenchmarks || !benchmarks) {
    return <p className="text-muted-foreground">Loading benchmarks...</p>;
  }

  const blendBenchmarks = benchmarks.filter((b) => activeIds.includes(b.id));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Blended Leaderboard</h1>
        <p className="text-muted-foreground">
          Min-max normalize scores within each benchmark, then weight and blend
          across benchmarks. Select a subset or adjust weights.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Benchmarks</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {benchmarks.map((b) => {
              const active = activeIds.includes(b.id);
              const selected = selectedIds.includes(b.id);
              return (
                <button
                  key={b.id}
                  onClick={() => toggleBenchmark(b.id)}
                  className={`rounded-full border px-3 py-1 text-sm transition-colors ${
                    selected
                      ? "border-primary bg-primary text-primary-foreground"
                      : active
                        ? "border-border bg-background hover:bg-accent"
                        : "border-dashed border-muted-foreground/30 text-muted-foreground hover:bg-accent"
                  }`}
                >
                  {b.name}
                </button>
              );
            })}
          </div>
          <p className="text-xs text-muted-foreground">
            {selectedIds.length === 0
              ? "Showing all benchmarks (click to narrow)."
              : `Blending ${selectedIds.length} benchmark${selectedIds.length === 1 ? "" : "s"}.`}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Weights</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2">
            {blendBenchmarks.map((b) => {
              const raw = weights[b.id] ?? 1;
              return (
                <label key={b.id} className="flex items-center gap-3 text-sm">
                  <span className="w-32 truncate">{b.name}</span>
                  <input
                    type="range"
                    min={0}
                    max={3}
                    step={0.1}
                    value={raw}
                    onChange={(e) =>
                      updateWeight(b.id, parseFloat(e.target.value))
                    }
                    className="flex-1"
                  />
                  <span className="w-10 text-right tabular-nums text-muted-foreground">
                    {raw.toFixed(1)}
                  </span>
                </label>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Ranking</CardTitle>
        </CardHeader>
        <CardContent>
          {blended === null ? (
            <p className="text-muted-foreground">Loading leaderboards...</p>
          ) : blended.length === 0 ? (
            <p className="text-muted-foreground">
              No results for the selected benchmarks.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">#</TableHead>
                  <TableHead>Model</TableHead>
                  <TableHead>Provider</TableHead>
                  <TableHead className="text-right">Blended Score</TableHead>
                  <TableHead className="text-right">Coverage</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {blended.map((row, i) => (
                  <TableRow key={row.model.id}>
                    <TableCell className="font-mono text-muted-foreground">
                      {i + 1}
                    </TableCell>
                    <TableCell>
                      <Link
                        to={`/models/${row.model.id}`}
                        className="font-medium hover:underline"
                      >
                        {row.model.name}
                      </Link>
                      {row.model.is_open_source && (
                        <Badge variant="secondary" className="ml-2">
                          OSS
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {row.model.provider.name}
                    </TableCell>
                    <TableCell className="text-right font-mono tabular-nums">
                      {row.blendedScore.toFixed(3)}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {activeIds.length - row.benchmarksMissing.length}/
                      {activeIds.length}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
