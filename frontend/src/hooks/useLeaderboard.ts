import { useQueries, useQuery } from "@tanstack/react-query";
import apiClient from "@/api/client";
import type { LeaderboardEntry } from "@/types";

async function fetchLeaderboard(benchmarkId: number): Promise<LeaderboardEntry[]> {
  const response = await apiClient.get(`/benchmarks/${benchmarkId}/leaderboard/`);
  return response.data;
}

export function useLeaderboard(benchmarkId: number | null) {
  return useQuery({
    queryKey: ["leaderboard", benchmarkId],
    queryFn: () => fetchLeaderboard(benchmarkId as number),
    enabled: benchmarkId != null,
  });
}

export function useLeaderboards(benchmarkIds: number[]) {
  return useQueries({
    queries: benchmarkIds.map((id) => ({
      queryKey: ["leaderboard", id],
      queryFn: () => fetchLeaderboard(id),
    })),
  });
}
