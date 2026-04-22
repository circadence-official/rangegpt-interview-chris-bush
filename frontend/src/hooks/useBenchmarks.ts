import { useQuery } from "@tanstack/react-query";
import apiClient from "@/api/client";
import type { Benchmark } from "@/types";

export function useBenchmarks() {
  return useQuery({
    queryKey: ["benchmarks"],
    queryFn: async (): Promise<Benchmark[]> => {
      const response = await apiClient.get("/benchmarks/");
      return response.data;
    },
  });
}
