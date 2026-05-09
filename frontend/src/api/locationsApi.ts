import { http } from "./client";
import type { Location } from "./types";

export interface LocationPayload {
  name: string;
  city: string;
  country: string;
  address?: string | null;
}

export class LocationsApi {
  async list(): Promise<Location[]> {
    const { data } = await http.get<Location[]>("/locations");
    return data;
  }

  async create(payload: LocationPayload): Promise<Location> {
    const { data } = await http.post<Location>("/locations", payload);
    return data;
  }

  async update(id: number, payload: Partial<LocationPayload>): Promise<Location> {
    const { data } = await http.patch<Location>(`/locations/${id}`, payload);
    return data;
  }

  async remove(id: number): Promise<void> {
    await http.delete(`/locations/${id}`);
  }
}

export const locationsApi = new LocationsApi();
