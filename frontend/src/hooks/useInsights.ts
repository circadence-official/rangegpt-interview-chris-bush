import { useQuery } from "@tanstack/react-query";
import type { AxiosError } from "axios";
import apiClient from "@/api/client";

export interface Insight {
  text: string;
  llm_model: string;
  cached: boolean;
}

function shouldRetry(failureCount: number, error: unknown): boolean {
  const axiosError = error as AxiosError | undefined;
  const status = axiosError?.response?.status;
  if (status === 503 || status === 404 || status === 400) return false;
  return failureCount < 1;
}

export function useModelInsight(modelId: number | null, enabled: boolean) {
  return useQuery({
    queryKey: ["insight", "model", modelId],
    queryFn: async (): Promise<Insight> => {
      const response = await apiClient.get(`/models/${modelId}/insight/`);
      return response.data;
    },
    enabled: enabled && modelId != null,
    retry: shouldRetry,
    staleTime: 5 * 60_000,
  });
}

export function useComparisonInsight(
  a: number | null,
  b: number | null,
  enabled: boolean,
) {
  const key = a != null && b != null ? [Math.min(a, b), Math.max(a, b)] : null;
  return useQuery({
    queryKey: ["insight", "comparison", key],
    queryFn: async (): Promise<Insight> => {
      const response = await apiClient.get("/insights/comparison/", {
        params: { a, b },
      });
      return response.data;
    },
    enabled: enabled && a != null && b != null && a !== b,
    retry: shouldRetry,
    staleTime: 5 * 60_000,
  });
}
