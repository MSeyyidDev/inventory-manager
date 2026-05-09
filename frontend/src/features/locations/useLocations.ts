import { useQuery } from "@tanstack/react-query";
import { locationsApi } from "@/api/locationsApi";

export function useLocations() {
  return useQuery({
    queryKey: ["locations"],
    queryFn: () => locationsApi.list(),
  });
}
