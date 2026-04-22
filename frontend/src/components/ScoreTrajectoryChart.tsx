import { useMemo } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { BenchmarkResultHistoryItem } from "@/types";

export interface TrajectorySeries {
  label: string;
  color: string;
  history: BenchmarkResultHistoryItem[];
}

interface Props {
  benchmarkId: number;
  series: TrajectorySeries[];
  height?: number;
}

interface Point {
  runAt: number;
  runAtLabel: string;
  [seriesKey: string]: number | string;
}

export default function ScoreTrajectoryChart({
  benchmarkId,
  series,
  height = 240,
}: Props) {
  const { data, seriesKeys } = useMemo(() => {
    const byTimestamp = new Map<number, Point>();
    const keys: { key: string; label: string; color: string }[] = [];

    series.forEach((s, i) => {
      const key = `series_${i}`;
      keys.push({ key, label: s.label, color: s.color });
      const filtered = s.history.filter((h) => h.benchmark.id === benchmarkId);
      for (const item of filtered) {
        const ts = new Date(item.run.run_at).getTime();
        const existing = byTimestamp.get(ts);
        const point = existing ?? {
          runAt: ts,
          runAtLabel: new Date(item.run.run_at).toLocaleDateString(),
        };
        point[key] = parseFloat(item.score);
        byTimestamp.set(ts, point);
      }
    });

    return {
      data: Array.from(byTimestamp.values()).sort((a, b) => a.runAt - b.runAt),
      seriesKeys: keys,
    };
  }, [benchmarkId, series]);

  if (data.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No history for this benchmark yet.
      </p>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="runAtLabel"
          fontSize={12}
          tickMargin={8}
          className="text-muted-foreground"
        />
        <YAxis
          domain={[0, 1]}
          fontSize={12}
          tickFormatter={(v) => v.toFixed(1)}
          className="text-muted-foreground"
        />
        <Tooltip
          contentStyle={{ fontSize: 12 }}
          formatter={(value) =>
            typeof value === "number" ? value.toFixed(4) : String(value)
          }
        />
        <Legend wrapperStyle={{ fontSize: 12 }} />
        {seriesKeys.map(({ key, label, color }) => (
          <Line
            key={key}
            type="monotone"
            dataKey={key}
            name={label}
            stroke={color}
            strokeWidth={2}
            dot={{ r: 3 }}
            connectNulls
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
