import { useQuery } from "@tanstack/react-query";
import { statsApi } from "@/api/statsApi";

export function useStats() {
  return useQuery({
    queryKey: ["stats-overview"],
    queryFn: () => statsApi.overview(),
  });
}
