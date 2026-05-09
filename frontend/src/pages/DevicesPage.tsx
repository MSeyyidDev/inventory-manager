import { useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "@/components/PageHeader";
import { Button } from "@/components/Button";
import { Badge } from "@/components/Badge";
import { Modal } from "@/components/Modal";
import { Select } from "@/components/Select";
import { DataTable, Column } from "@/components/DataTable";
import { Pagination } from "@/components/Pagination";
import { devicesApi } from "@/api/devicesApi";
import { useDevices } from "@/features/devices/useDevices";
import { useLocations } from "@/features/locations/useLocations";
import { DeviceForm } from "@/features/devices/DeviceForm";
import { AssignDeviceModal } from "@/features/assignments/AssignDeviceModal";
import type { Device, DevicePayload } from "@/api/types";

const PAGE_SIZE = 25;

const STATUS_OPTIONS = [
  { value: "available", label: "Available" },
  { value: "assigned", label: "Assigned" },
  { value: "maintenance", label: "Maintenance" },
  { value: "retired", label: "Retired" },
];
const TYPE_OPTIONS = [
  { value: "laptop", label: "Laptop" },
  { value: "monitor", label: "Monitor" },
  { value: "smartphone", label: "Smartphone" },
  { value: "server", label: "Server" },
  { value: "accessory", label: "Accessory" },
];

export function DevicesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const fileInput = useRef<HTMLInputElement | null>(null);

  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [type, setType] = useState<string>("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [sortBy, setSortBy] = useState("id");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc");

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Device | null>(null);

  const [assignTarget, setAssignTarget] = useState<Device | null>(null);
  const [importMessage, setImportMessage] = useState<string | null>(null);

  const query = useMemo(
    () => ({
      page,
      page_size: PAGE_SIZE,
      search: search || undefined,
      type: type || undefined,
      status: statusFilter || undefined,
      sort_by: sortBy,
      sort_dir: sortDir,
    }),
    [page, search, type, statusFilter, sortBy, sortDir]
  );

  const devices = useDevices(query);
  const locations = useLocations();

  const create = useMutation({
    mutationFn: (payload: DevicePayload) => devicesApi.create(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["devices"] });
      queryClient.invalidateQueries({ queryKey: ["stats-overview"] });
      setModalOpen(false);
    },
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: Partial<DevicePayload> }) =>
      devicesApi.update(id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["devices"] });
      setModalOpen(false);
      setEditing(null);
    },
  });
  const remove = useMutation({
    mutationFn: (id: number) => devicesApi.remove(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["devices"] });
      queryClient.invalidateQueries({ queryKey: ["stats-overview"] });
    },
  });

  function handleSort(key: string) {
    if (sortBy === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(key);
      setSortDir("asc");
    }
  }

  async function handleImport(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const result = await devicesApi.importCsv(file);
      setImportMessage(
        `Created ${result.created}, skipped ${result.skipped}, errors ${result.errors.length}`
      );
      queryClient.invalidateQueries({ queryKey: ["devices"] });
      queryClient.invalidateQueries({ queryKey: ["stats-overview"] });
    } catch (err) {
      setImportMessage((err as Error).message);
    } finally {
      e.target.value = "";
    }
  }

  const columns: Column<Device>[] = [
    { key: "id", header: "ID", render: (d) => d.id, sortable: true, className: "w-16" },
    {
      key: "type",
      header: "Type",
      render: (d) => <span className="capitalize">{d.type}</span>,
      sortable: true,
    },
    {
      key: "manufacturer",
      header: "Manufacturer",
      render: (d) => d.manufacturer,
      sortable: true,
    },
    { key: "model", header: "Model", render: (d) => d.model, sortable: true },
    {
      key: "serial_number",
      header: "Serial",
      render: (d) => <span className="font-mono text-xs">{d.serial_number}</span>,
      sortable: true,
    },
    {
      key: "status",
      header: "Status",
      render: (d) => <Badge status={d.status}>{d.status}</Badge>,
      sortable: true,
    },
    {
      key: "assigned",
      header: "Assigned to",
      render: (d) => d.assigned_to_name ?? <span className="text-slate-400">—</span>,
    },
    {
      key: "actions",
      header: "",
      className: "w-48 text-right",
      render: (d) => (
        <div className="flex justify-end gap-2" onClick={(e) => e.stopPropagation()}>
          {d.status !== "assigned" && d.status !== "retired" ? (
            <Button variant="ghost" onClick={() => setAssignTarget(d)}>
              Assign
            </Button>
          ) : null}
          <Button
            variant="ghost"
            onClick={() => {
              setEditing(d);
              setModalOpen(true);
            }}
          >
            Edit
          </Button>
          <Button
            variant="ghost"
            onClick={() => {
              if (confirm(`Delete ${d.serial_number}?`)) remove.mutate(d.id);
            }}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Devices"
        subtitle="Manage every laptop, monitor, phone, server and accessory."
        actions={
          <>
            <input
              ref={fileInput}
              type="file"
              accept=".csv"
              hidden
              onChange={handleImport}
            />
            <Button variant="secondary" onClick={() => fileInput.current?.click()}>
              Import CSV
            </Button>
            <a
              className="btn-secondary"
              href={devicesApi.exportCsvUrl()}
              download="devices.csv"
            >
              Export CSV
            </a>
            <Button
              onClick={() => {
                setEditing(null);
                setModalOpen(true);
              }}
            >
              New device
            </Button>
          </>
        }
      />

      {importMessage ? (
        <div className="card mb-4 border-brand-200 bg-brand-50 text-brand-800 dark:bg-brand-900/20 dark:text-brand-200">
          {importMessage}
        </div>
      ) : null}

      <div className="card mb-4 flex flex-wrap items-end gap-3">
        <label className="flex flex-1 min-w-[200px] flex-col gap-1 text-sm">
          <span className="text-slate-500">Search</span>
          <input
            className="input"
            placeholder="Serial, model or manufacturer…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-500">Type</span>
          <Select
            value={type}
            placeholder="All types"
            options={TYPE_OPTIONS}
            onChange={(e) => {
              setType(e.target.value);
              setPage(1);
            }}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-500">Status</span>
          <Select
            value={statusFilter}
            placeholder="Any status"
            options={STATUS_OPTIONS}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setPage(1);
            }}
          />
        </label>
      </div>

      <DataTable<Device>
        columns={columns}
        rows={devices.data?.items ?? []}
        rowKey={(d) => d.id}
        loading={devices.isLoading}
        sortBy={sortBy}
        sortDir={sortDir}
        onSortChange={handleSort}
        onRowClick={(d) => navigate(`/devices/${d.id}`)}
      />

      <div className="mt-4">
        <Pagination
          page={page}
          pageSize={PAGE_SIZE}
          total={devices.data?.total ?? 0}
          onPageChange={setPage}
        />
      </div>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? `Edit ${editing.model}` : "New device"}
      >
        <DeviceForm
          initial={editing}
          locations={(locations.data ?? []).map((l) => ({ id: l.id, name: l.name }))}
          submitting={create.isPending || update.isPending}
          onCancel={() => setModalOpen(false)}
          onSubmit={async (payload) => {
            if (editing) await update.mutateAsync({ id: editing.id, payload });
            else await create.mutateAsync(payload);
          }}
        />
      </Modal>

      <AssignDeviceModal
        device={assignTarget}
        open={assignTarget !== null}
        onClose={() => setAssignTarget(null)}
      />
    </div>
  );
}

