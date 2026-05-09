import { http } from "./client";
import type { Assignment, Device, DevicePayload, Page } from "./types";

export interface DeviceQuery {
  page?: number;
  page_size?: number;
  type?: string;
  status?: string;
  location_id?: number;
  assigned_to?: number;
  search?: string;
  sort_by?: string;
  sort_dir?: "asc" | "desc";
}

export class DevicesApi {
  async list(query: DeviceQuery = {}): Promise<Page<Device>> {
    const { data } = await http.get<Page<Device>>("/devices", { params: query });
    return data;
  }

  async get(id: number): Promise<Device> {
    const { data } = await http.get<Device>(`/devices/${id}`);
    return data;
  }

  async history(id: number): Promise<Assignment[]> {
    const { data } = await http.get<Assignment[]>(`/devices/${id}/history`);
    return data;
  }

  async create(payload: DevicePayload): Promise<Device> {
    const { data } = await http.post<Device>("/devices", payload);
    return data;
  }

  async update(id: number, payload: Partial<DevicePayload>): Promise<Device> {
    const { data } = await http.patch<Device>(`/devices/${id}`, payload);
    return data;
  }

  async remove(id: number): Promise<void> {
    await http.delete(`/devices/${id}`);
  }

  exportCsvUrl(): string {
    return `${http.defaults.baseURL}/devices/export-csv`;
  }

  async importCsv(file: File): Promise<{ created: number; skipped: number; errors: string[] }> {
    const form = new FormData();
    form.append("file", file);
    const { data } = await http.post("/devices/import-csv", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  }
}

export const devicesApi = new DevicesApi();
