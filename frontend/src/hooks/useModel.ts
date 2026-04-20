import { useQuery } from "@tanstack/react-query";
import apiClient from "@/api/client";
import type { LLMModel } from "@/types";

export function useModel(id: number) {
  return useQuery({
    queryKey: ["models", id],
    queryFn: async (): Promise<LLMModel> => {
      const response = await apiClient.get(`/models/${id}/`);
      return response.data;
    },
    enabled: !!id,
  });
}
