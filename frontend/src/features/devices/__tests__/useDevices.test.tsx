import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { useDevices } from "../useDevices";
import { devicesApi } from "@/api/devicesApi";

vi.mock("@/api/devicesApi", () => ({
  devicesApi: {
    list: vi.fn(),
  },
}));

const wrapper = () => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={client}>{children}</QueryClientProvider>
  );
};

describe("useDevices", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("fetches devices using the supplied query", async () => {
    (devicesApi.list as ReturnType<typeof vi.fn>).mockResolvedValue({
      items: [],
      total: 0,
      page: 1,
      page_size: 25,
    });
    const { result } = renderHook(() => useDevices({ page: 1, page_size: 25 }), {
      wrapper: wrapper(),
    });
    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(devicesApi.list).toHaveBeenCalledWith({ page: 1, page_size: 25 });
  });
});
