import { useQuery } from "@tanstack/react-query";
import apiClient from "@/api/client";
import type { LLMModelListItem } from "@/types";

export function useModels() {
  return useQuery({
    queryKey: ["models"],
    queryFn: async (): Promise<LLMModelListItem[]> => {
      const response = await apiClient.get("/models/");
      return response.data;
    },
  });
}
