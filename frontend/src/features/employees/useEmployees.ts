import { useQuery } from "@tanstack/react-query";
import { employeesApi, EmployeeQuery } from "@/api/employeesApi";

export function useEmployees(query: EmployeeQuery) {
  return useQuery({
    queryKey: ["employees", query],
    queryFn: () => employeesApi.list(query),
  });
}

export function useEmployee(id: number | undefined) {
  return useQuery({
    queryKey: ["employee", id],
    queryFn: () => employeesApi.get(id as number),
    enabled: id != null,
  });
}

export function useEmployeeDevices(id: number | undefined) {
  return useQuery({
    queryKey: ["employee-devices", id],
    queryFn: () => employeesApi.devices(id as number),
    enabled: id != null,
  });
}
