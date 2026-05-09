import { http } from "./client";
import type { StatsOverview } from "./types";

export class StatsApi {
  async overview(): Promise<StatsOverview> {
    const { data } = await http.get<StatsOverview>("/stats/overview");
    return data;
  }
}

export const statsApi = new StatsApi();
