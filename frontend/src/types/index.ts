export interface Provider {
  id: number;
  name: string;
  website: string;
}

export interface LLMModel {
  id: number;
  provider: Provider;
  name: string;
  description: string;
  context_window: number;
  input_price_per_1m: string;
  output_price_per_1m: string;
  arena_elo_score: number | null;
  release_date: string;
  is_open_source: boolean;
  created_at: string;
  updated_at: string;
}

export interface LLMModelListItem {
  id: number;
  provider: Provider;
  name: string;
  context_window: number;
  input_price_per_1m: string;
  output_price_per_1m: string;
  arena_elo_score: number | null;
  release_date: string;
  is_open_source: boolean;
}

export interface Benchmark {
  id: number;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface BenchmarkRef {
  id: number;
  name: string;
}

export interface BenchmarkRunRef {
  id: number;
  run_at: string;
}

export interface LeaderboardModel {
  id: number;
  name: string;
  provider: Provider;
  is_open_source: boolean;
}

export interface LeaderboardEntry {
  model: LeaderboardModel;
  score: string;
  measured_at: string;
}

export interface BenchmarkSummaryEntry {
  benchmark: BenchmarkRef;
  score: string;
  measured_at: string;
}

export interface BenchmarkResultHistoryItem {
  id: number;
  benchmark: BenchmarkRef;
  run: BenchmarkRunRef;
  score: string;
  created_at: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
