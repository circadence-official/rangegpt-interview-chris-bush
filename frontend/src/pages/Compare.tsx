import { useMemo, useState } from "react";
import { useModels } from "@/hooks/useModels";
import { useModel } from "@/hooks/useModel";
import {
  useModelBenchmarkResults,
  useModelBenchmarkSummary,
} from "@/hooks/useModelBenchmarks";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import ScoreTrajectoryChart from "@/components/ScoreTrajectoryChart";
import type {
  BenchmarkResultHistoryItem,
  BenchmarkSummaryEntry,
} from "@/types";

const SERIES_COLORS = ["#2563eb", "#dc2626"] as const;

export default function Compare() {
  const { data: models } = useModels();
  const [idA, setIdA] = useState<number | null>(null);
  const [idB, setIdB] = useState<number | null>(null);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Compare Models</h1>
        <p className="text-muted-foreground">
          Side-by-side specs, per-benchmark latest scores, and score trajectory
          over time.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-4 pt-6 sm:flex-row">
          <ModelPicker
            label="Model A"
            value={idA}
            onChange={setIdA}
            models={models ?? []}
            disabledId={idB}
            color={SERIES_COLORS[0]}
          />
          <ModelPicker
            label="Model B"
            value={idB}
            onChange={setIdB}
            models={models ?? []}
            disabledId={idA}
            color={SERIES_COLORS[1]}
          />
        </CardContent>
      </Card>

      {idA && idB ? (
        <ComparisonPanels idA={idA} idB={idB} />
      ) : (
        <p className="text-muted-foreground">
          Pick two models to compare.
        </p>
      )}
    </div>
  );
}

interface PickerProps {
  label: string;
  value: number | null;
  onChange: (id: number) => void;
  models: { id: number; name: string; provider: { name: string } }[];
  disabledId: number | null;
  color: string;
}

function ModelPicker({
  label,
  value,
  onChange,
  models,
  disabledId,
  color,
}: PickerProps) {
  return (
    <div className="flex-1 space-y-1.5">
      <div className="flex items-center gap-2 text-sm font-medium">
        <span
          className="inline-block h-2.5 w-2.5 rounded-full"
          style={{ backgroundColor: color }}
        />
        {label}
      </div>
      <Select
        value={value ? String(value) : undefined}
        onValueChange={(v) => onChange(Number(v))}
      >
        <SelectTrigger>
          <SelectValue placeholder="Select a model" />
        </SelectTrigger>
        <SelectContent>
          {models.map((m) => (
            <SelectItem
              key={m.id}
              value={String(m.id)}
              disabled={m.id === disabledId}
            >
              {m.provider.name} · {m.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

function ComparisonPanels({ idA, idB }: { idA: number; idB: number }) {
  const modelA = useModel(idA);
  const modelB = useModel(idB);
  const summaryA = useModelBenchmarkSummary(idA);
  const summaryB = useModelBenchmarkSummary(idB);
  const historyA = useModelBenchmarkResults(idA);
  const historyB = useModelBenchmarkResults(idB);

  if (modelA.isLoading || modelB.isLoading || !modelA.data || !modelB.data) {
    return <p className="text-muted-foreground">Loading comparison...</p>;
  }

  const a = modelA.data;
  const b = modelB.data;

  const historyAItems: BenchmarkResultHistoryItem[] = historyA.data?.results ?? [];
  const historyBItems: BenchmarkResultHistoryItem[] = historyB.data?.results ?? [];

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Specs</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead></TableHead>
                <TableHead>
                  <span
                    className="mr-2 inline-block h-2 w-2 rounded-full"
                    style={{ backgroundColor: SERIES_COLORS[0] }}
                  />
                  {a.name}
                </TableHead>
                <TableHead>
                  <span
                    className="mr-2 inline-block h-2 w-2 rounded-full"
                    style={{ backgroundColor: SERIES_COLORS[1] }}
                  />
                  {b.name}
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <SpecRow label="Provider" a={a.provider.name} b={b.provider.name} />
              <SpecRow
                label="Context window"
                a={`${(a.context_window / 1000).toLocaleString()}K`}
                b={`${(b.context_window / 1000).toLocaleString()}K`}
              />
              <SpecRow
                label="Input $/1M"
                a={`$${parseFloat(a.input_price_per_1m)}`}
                b={`$${parseFloat(b.input_price_per_1m)}`}
              />
              <SpecRow
                label="Output $/1M"
                a={`$${parseFloat(a.output_price_per_1m)}`}
                b={`$${parseFloat(b.output_price_per_1m)}`}
              />
              <SpecRow
                label="Arena ELO"
                a={a.arena_elo_score ?? "—"}
                b={b.arena_elo_score ?? "—"}
              />
              <SpecRow label="Released" a={a.release_date} b={b.release_date} />
              <SpecRow
                label="Open source"
                a={a.is_open_source ? "Yes" : "No"}
                b={b.is_open_source ? "Yes" : "No"}
              />
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Latest benchmark scores</CardTitle>
        </CardHeader>
        <CardContent>
          <BenchmarkComparisonTable
            a={summaryA.data ?? []}
            b={summaryB.data ?? []}
            nameA={a.name}
            nameB={b.name}
          />
        </CardContent>
      </Card>

      <TrajectoryCards
        historyA={historyAItems}
        historyB={historyBItems}
        nameA={a.name}
        nameB={b.name}
      />
    </>
  );
}

function SpecRow({
  label,
  a,
  b,
}: {
  label: string;
  a: string | number;
  b: string | number;
}) {
  const winner =
    typeof a === "number" && typeof b === "number"
      ? a === b
        ? null
        : a > b
          ? "a"
          : "b"
      : null;
  return (
    <TableRow>
      <TableCell className="text-muted-foreground">{label}</TableCell>
      <TableCell className={winner === "a" ? "font-semibold" : ""}>{a}</TableCell>
      <TableCell className={winner === "b" ? "font-semibold" : ""}>{b}</TableCell>
    </TableRow>
  );
}

function BenchmarkComparisonTable({
  a,
  b,
  nameA,
  nameB,
}: {
  a: BenchmarkSummaryEntry[];
  b: BenchmarkSummaryEntry[];
  nameA: string;
  nameB: string;
}) {
  const byBenchmark = new Map<
    number,
    { name: string; scoreA: number | null; scoreB: number | null }
  >();
  for (const entry of a) {
    byBenchmark.set(entry.benchmark.id, {
      name: entry.benchmark.name,
      scoreA: parseFloat(entry.score),
      scoreB: null,
    });
  }
  for (const entry of b) {
    const row = byBenchmark.get(entry.benchmark.id) ?? {
      name: entry.benchmark.name,
      scoreA: null,
      scoreB: null,
    };
    row.scoreB = parseFloat(entry.score);
    byBenchmark.set(entry.benchmark.id, row);
  }

  const rows = Array.from(byBenchmark.entries()).sort(([, x], [, y]) =>
    x.name.localeCompare(y.name),
  );

  if (rows.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Neither model has benchmark results.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Benchmark</TableHead>
          <TableHead className="text-right">{nameA}</TableHead>
          <TableHead className="text-right">{nameB}</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map(([id, row]) => {
          const winner =
            row.scoreA != null && row.scoreB != null
              ? row.scoreA === row.scoreB
                ? null
                : row.scoreA > row.scoreB
                  ? "a"
                  : "b"
              : null;
          return (
            <TableRow key={id}>
              <TableCell>{row.name}</TableCell>
              <TableCell
                className={`text-right font-mono tabular-nums ${
                  winner === "a" ? "font-semibold" : ""
                }`}
              >
                {row.scoreA != null ? row.scoreA.toFixed(4) : "—"}
              </TableCell>
              <TableCell
                className={`text-right font-mono tabular-nums ${
                  winner === "b" ? "font-semibold" : ""
                }`}
              >
                {row.scoreB != null ? row.scoreB.toFixed(4) : "—"}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
}

function TrajectoryCards({
  historyA,
  historyB,
  nameA,
  nameB,
}: {
  historyA: BenchmarkResultHistoryItem[];
  historyB: BenchmarkResultHistoryItem[];
  nameA: string;
  nameB: string;
}) {
  const benchmarks = useMemo(() => {
    const map = new Map<number, string>();
    for (const item of [...historyA, ...historyB]) {
      map.set(item.benchmark.id, item.benchmark.name);
    }
    return Array.from(map.entries()).sort(([, a], [, b]) => a.localeCompare(b));
  }, [historyA, historyB]);

  if (benchmarks.length === 0) {
    return null;
  }

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      {benchmarks.map(([id, name]) => (
        <Card key={id}>
          <CardHeader>
            <CardTitle className="text-base">{name}</CardTitle>
          </CardHeader>
          <CardContent>
            <ScoreTrajectoryChart
              benchmarkId={id}
              series={[
                { label: nameA, color: SERIES_COLORS[0], history: historyA },
                { label: nameB, color: SERIES_COLORS[1], history: historyB },
              ]}
            />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

