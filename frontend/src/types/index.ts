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
