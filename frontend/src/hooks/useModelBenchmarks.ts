import { useQuery } from "@tanstack/react-query";
import apiClient from "@/api/client";
import type {
  BenchmarkResultHistoryItem,
  BenchmarkSummaryEntry,
  Paginated,
} from "@/types";

export function useModelBenchmarkSummary(modelId: number | null) {
  return useQuery({
    queryKey: ["models", modelId, "benchmark-summary"],
    queryFn: async (): Promise<BenchmarkSummaryEntry[]> => {
      const response = await apiClient.get(
        `/models/${modelId}/benchmark-summary/`,
      );
      return response.data;
    },
    enabled: modelId != null,
  });
}

export function useModelBenchmarkResults(modelId: number | null) {
  return useQuery({
    queryKey: ["models", modelId, "benchmark-results"],
    queryFn: async (): Promise<Paginated<BenchmarkResultHistoryItem>> => {
      const response = await apiClient.get(
        `/models/${modelId}/benchmark-results/`,
        { params: { page_size: 200 } },
      );
      return response.data;
    },
    enabled: modelId != null,
  });
}
