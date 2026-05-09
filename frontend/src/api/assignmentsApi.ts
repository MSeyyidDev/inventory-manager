import { http } from "./client";
import type { Assignment } from "./types";

export class AssignmentsApi {
  async assign(payload: {
    device_id: number;
    employee_id: number;
    note?: string;
  }): Promise<Assignment> {
    const { data } = await http.post<Assignment>("/assignments", payload);
    return data;
  }

  async returnAssignment(id: number, note?: string): Promise<Assignment> {
    const { data } = await http.post<Assignment>(`/assignments/${id}/return`, { note });
    return data;
  }
}

export const assignmentsApi = new AssignmentsApi();
