import { http } from "./client";
import type { Assignment, Employee, EmployeePayload, Page } from "./types";

export interface EmployeeQuery {
  page?: number;
  page_size?: number;
  search?: string;
  department?: string;
}

export class EmployeesApi {
  async list(query: EmployeeQuery = {}): Promise<Page<Employee>> {
    const { data } = await http.get<Page<Employee>>("/employees", { params: query });
    return data;
  }

  async get(id: number): Promise<Employee> {
    const { data } = await http.get<Employee>(`/employees/${id}`);
    return data;
  }

  async devices(id: number): Promise<Assignment[]> {
    const { data } = await http.get<Assignment[]>(`/employees/${id}/devices`);
    return data;
  }

  async create(payload: EmployeePayload): Promise<Employee> {
    const { data } = await http.post<Employee>("/employees", payload);
    return data;
  }

  async update(id: number, payload: Partial<EmployeePayload>): Promise<Employee> {
    const { data } = await http.patch<Employee>(`/employees/${id}`, payload);
    return data;
  }

  async remove(id: number): Promise<void> {
    await http.delete(`/employees/${id}`);
  }
}

export const employeesApi = new EmployeesApi();
