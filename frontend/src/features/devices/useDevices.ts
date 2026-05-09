import { useQuery } from "@tanstack/react-query";
import { devicesApi, DeviceQuery } from "@/api/devicesApi";

export function useDevices(query: DeviceQuery) {
  return useQuery({
    queryKey: ["devices", query],
    queryFn: () => devicesApi.list(query),
  });
}

export function useDevice(id: number | undefined) {
  return useQuery({
    queryKey: ["device", id],
    queryFn: () => devicesApi.get(id as number),
    enabled: id != null,
  });
}

export function useDeviceHistory(id: number | undefined) {
  return useQuery({
    queryKey: ["device-history", id],
    queryFn: () => devicesApi.history(id as number),
    enabled: id != null,
  });
}
