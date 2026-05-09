import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DeviceForm } from "../DeviceForm";

describe("DeviceForm", () => {
  it("validates required fields", async () => {
    const onSubmit = vi.fn();
    render(
      <DeviceForm
        locations={[]}
        onSubmit={onSubmit}
        onCancel={() => {}}
      />
    );
    await userEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(screen.getByText(/manufacturer is required/i)).toBeInTheDocument();
    });
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("submits a valid payload", async () => {
    const onSubmit = vi.fn();
    render(
      <DeviceForm
        locations={[{ id: 1, name: "Berlin HQ" }]}
        onSubmit={onSubmit}
        onCancel={() => {}}
      />
    );
    await userEvent.type(screen.getByLabelText(/manufacturer/i), "Dell");
    await userEvent.type(screen.getByLabelText(/^model$/i), "Latitude 7440");
    await userEvent.type(screen.getByLabelText(/serial number/i), "DLL-1");
    await userEvent.click(screen.getByRole("button", { name: /save/i }));
    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledOnce();
    });
    const payload = onSubmit.mock.calls[0][0];
    expect(payload.manufacturer).toBe("Dell");
    expect(payload.serial_number).toBe("DLL-1");
  });

  it("renders existing values when editing", () => {
    render(
      <DeviceForm
        initial={{
          id: 1,
          type: "monitor",
          manufacturer: "LG",
          model: "27UP",
          serial_number: "LG-001",
          status: "available",
          purchase_date: null,
          warranty_end: null,
          notes: null,
          location_id: null,
          assigned_to_id: null,
          assigned_to_name: null,
        }}
        locations={[]}
        onSubmit={() => {}}
        onCancel={() => {}}
      />
    );
    expect(screen.getByDisplayValue("LG")).toBeInTheDocument();
    expect(screen.getByDisplayValue("27UP")).toBeInTheDocument();
  });
});
