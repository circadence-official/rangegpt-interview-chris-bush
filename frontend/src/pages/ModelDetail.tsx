import { useMemo, useState } from "react";
import { useParams, Link } from "react-router";
import { useModel } from "@/hooks/useModel";
import {
  useModelBenchmarkResults,
  useModelBenchmarkSummary,
} from "@/hooks/useModelBenchmarks";
import { useModelInsight } from "@/hooks/useInsights";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import InsightCard from "@/components/InsightCard";
import ScoreTrajectoryChart from "@/components/ScoreTrajectoryChart";

const CHART_COLOR = "#2563eb";

export default function ModelDetail() {
  const { id } = useParams();
  const modelId = Number(id);
  const { data: model, isLoading, error } = useModel(modelId);
  const summary = useModelBenchmarkSummary(modelId);
  const history = useModelBenchmarkResults(modelId);
  const [insightEnabled, setInsightEnabled] = useState(false);
  const insight = useModelInsight(modelId, insightEnabled);

  const benchmarksInHistory = useMemo(() => {
    const map = new Map<number, string>();
    for (const item of history.data?.results ?? []) {
      map.set(item.benchmark.id, item.benchmark.name);
    }
    return Array.from(map.entries()).sort(([, a], [, b]) =>
      a.localeCompare(b),
    );
  }, [history.data]);

  if (isLoading) {
    return <p className="text-muted-foreground">Loading model...</p>;
  }

  if (error || !model) {
    return <p className="text-destructive">Model not found.</p>;
  }

  return (
    <div>
      <div className="mb-6">
        <Button variant="ghost" asChild>
          <Link to="/">&larr; Back to models</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">{model.name}</CardTitle>
              <p className="text-muted-foreground">{model.provider.name}</p>
            </div>
            <div className="flex gap-1.5">
              {model.is_open_source && (
                <Badge variant="secondary">Open Source</Badge>
              )}
              {model.arena_elo_score && (
                <Badge variant="outline">ELO {model.arena_elo_score}</Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {model.description && (
            <div>
              <h3 className="mb-1 text-sm font-medium text-muted-foreground">
                Description
              </h3>
              <p>{model.description}</p>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-sm text-muted-foreground">Context Window</p>
              <p className="text-lg font-medium">
                {(model.context_window / 1000).toLocaleString()}K tokens
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Input Price</p>
              <p className="text-lg font-medium">
                ${parseFloat(model.input_price_per_1m)}/1M tokens
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Output Price</p>
              <p className="text-lg font-medium">
                ${parseFloat(model.output_price_per_1m)}/1M tokens
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Release Date</p>
              <p className="text-lg font-medium">{model.release_date}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="mt-6">
        <InsightCard
          title="AI summary"
          query={insight}
          enabled={insightEnabled}
          setEnabled={setInsightEnabled}
        />
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-lg">Latest benchmark scores</CardTitle>
        </CardHeader>
        <CardContent>
          {summary.isLoading ? (
            <p className="text-sm text-muted-foreground">Loading scores...</p>
          ) : (summary.data?.length ?? 0) === 0 ? (
            <p className="text-sm text-muted-foreground">
              No benchmark results for this model yet.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Benchmark</TableHead>
                  <TableHead className="text-right">Score</TableHead>
                  <TableHead className="text-right">Measured</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {summary.data?.map((entry) => (
                  <TableRow key={entry.benchmark.id}>
                    <TableCell>{entry.benchmark.name}</TableCell>
                    <TableCell className="text-right font-mono tabular-nums">
                      {parseFloat(entry.score).toFixed(4)}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {new Date(entry.measured_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {benchmarksInHistory.length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">Score trajectory</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 lg:grid-cols-2">
              {benchmarksInHistory.map(([id, name]) => (
                <div key={id}>
                  <h3 className="mb-2 text-sm font-medium">{name}</h3>
                  <ScoreTrajectoryChart
                    benchmarkId={id}
                    series={[
                      {
                        label: model.name,
                        color: CHART_COLOR,
                        history: history.data?.results ?? [],
                      },
                    ]}
                  />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
