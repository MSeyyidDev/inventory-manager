import { useState } from "react";
import { z } from "zod";
import { Button } from "@/components/Button";
import { Select } from "@/components/Select";
import type { Device, DevicePayload, DeviceStatus, DeviceType } from "@/api/types";

const deviceSchema = z.object({
  type: z.enum(["laptop", "monitor", "smartphone", "server", "accessory"]),
  manufacturer: z.string().min(1, "Manufacturer is required"),
  model: z.string().min(1, "Model is required"),
  serial_number: z.string().min(1, "Serial number is required"),
  status: z.enum(["available", "assigned", "maintenance", "retired"]),
  purchase_date: z.string().optional().nullable(),
  warranty_end: z.string().optional().nullable(),
  notes: z.string().optional().nullable(),
  location_id: z.number().int().positive().optional().nullable(),
});

const TYPE_OPTIONS: { value: DeviceType; label: string }[] = [
  { value: "laptop", label: "Laptop" },
  { value: "monitor", label: "Monitor" },
  { value: "smartphone", label: "Smartphone" },
  { value: "server", label: "Server" },
  { value: "accessory", label: "Accessory" },
];

const STATUS_OPTIONS: { value: DeviceStatus; label: string }[] = [
  { value: "available", label: "Available" },
  { value: "assigned", label: "Assigned" },
  { value: "maintenance", label: "Maintenance" },
  { value: "retired", label: "Retired" },
];

interface DeviceFormProps {
  initial?: Device | null;
  locations: { id: number; name: string }[];
  onSubmit: (payload: DevicePayload) => Promise<void> | void;
  onCancel: () => void;
  submitting?: boolean;
}

export function DeviceForm({ initial, locations, onSubmit, onCancel, submitting }: DeviceFormProps) {
  const [form, setForm] = useState<DevicePayload>({
    type: initial?.type ?? "laptop",
    manufacturer: initial?.manufacturer ?? "",
    model: initial?.model ?? "",
    serial_number: initial?.serial_number ?? "",
    status: initial?.status ?? "available",
    purchase_date: initial?.purchase_date ?? null,
    warranty_end: initial?.warranty_end ?? null,
    notes: initial?.notes ?? null,
    location_id: initial?.location_id ?? null,
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  function update<K extends keyof DevicePayload>(key: K, value: DevicePayload[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const parsed = deviceSchema.safeParse(form);
    if (!parsed.success) {
      const fieldErrors: Record<string, string> = {};
      for (const issue of parsed.error.issues) {
        fieldErrors[issue.path.join(".")] = issue.message;
      }
      setErrors(fieldErrors);
      return;
    }
    setErrors({});
    await onSubmit(parsed.data as DevicePayload);
  }

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
      <Field label="Type" error={errors.type}>
        <Select
          value={form.type}
          options={TYPE_OPTIONS}
          onChange={(e) => update("type", e.target.value as DeviceType)}
        />
      </Field>
      <Field label="Status" error={errors.status}>
        <Select
          value={form.status}
          options={STATUS_OPTIONS}
          onChange={(e) => update("status", e.target.value as DeviceStatus)}
        />
      </Field>
      <Field label="Manufacturer" error={errors.manufacturer}>
        <input
          className="input"
          value={form.manufacturer}
          onChange={(e) => update("manufacturer", e.target.value)}
        />
      </Field>
      <Field label="Model" error={errors.model}>
        <input
          className="input"
          value={form.model}
          onChange={(e) => update("model", e.target.value)}
        />
      </Field>
      <Field label="Serial number" error={errors.serial_number}>
        <input
          className="input"
          value={form.serial_number}
          onChange={(e) => update("serial_number", e.target.value)}
        />
      </Field>
      <Field label="Location">
        <Select
          value={form.location_id ? String(form.location_id) : ""}
          placeholder="Unassigned"
          options={locations.map((l) => ({ value: String(l.id), label: l.name }))}
          onChange={(e) =>
            update("location_id", e.target.value ? Number(e.target.value) : null)
          }
        />
      </Field>
      <Field label="Purchase date">
        <input
          type="date"
          className="input"
          value={form.purchase_date ?? ""}
          onChange={(e) => update("purchase_date", e.target.value || null)}
        />
      </Field>
      <Field label="Warranty end">
        <input
          type="date"
          className="input"
          value={form.warranty_end ?? ""}
          onChange={(e) => update("warranty_end", e.target.value || null)}
        />
      </Field>
      <div className="col-span-2">
        <Field label="Notes">
          <textarea
            className="input min-h-[80px] py-2"
            value={form.notes ?? ""}
            onChange={(e) => update("notes", e.target.value || null)}
          />
        </Field>
      </div>
      <div className="col-span-2 flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : "Save"}
        </Button>
      </div>
    </form>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="flex flex-col gap-1 text-sm">
      <span className="font-medium text-slate-700 dark:text-slate-300">{label}</span>
      {children}
      {error ? <span className="text-xs text-red-600">{error}</span> : null}
    </label>
  );
}
