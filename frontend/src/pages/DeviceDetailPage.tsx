import { Link, useParams } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/Badge";
import { Button } from "@/components/Button";
import { useDevice, useDeviceHistory } from "@/features/devices/useDevices";
import { assignmentsApi } from "@/api/assignmentsApi";

export function DeviceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const numericId = id ? Number(id) : undefined;
  const queryClient = useQueryClient();
  const device = useDevice(numericId);
  const history = useDeviceHistory(numericId);

  const returnAssignment = useMutation({
    mutationFn: (assignmentId: number) => assignmentsApi.returnAssignment(assignmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["device", numericId] });
      queryClient.invalidateQueries({ queryKey: ["device-history", numericId] });
      queryClient.invalidateQueries({ queryKey: ["devices"] });
      queryClient.invalidateQueries({ queryKey: ["stats-overview"] });
    },
  });

  if (device.isLoading) return <div>Loading…</div>;
  if (device.error || !device.data) return <div>Device not found.</div>;

  const d = device.data;

  return (
    <div>
      <PageHeader
        title={`${d.manufacturer} ${d.model}`}
        subtitle={d.serial_number}
        actions={
          <Link to="/devices" className="btn-secondary">
            Back to devices
          </Link>
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-1">
          <h3 className="mb-3 font-medium">Specifications</h3>
          <dl className="space-y-2 text-sm">
            <Row label="Type">{d.type}</Row>
            <Row label="Status">
              <Badge status={d.status}>{d.status}</Badge>
            </Row>
            <Row label="Manufacturer">{d.manufacturer}</Row>
            <Row label="Model">{d.model}</Row>
            <Row label="Serial">
              <span className="font-mono">{d.serial_number}</span>
            </Row>
            <Row label="Purchase">{d.purchase_date ?? "—"}</Row>
            <Row label="Warranty end">{d.warranty_end ?? "—"}</Row>
            <Row label="Assigned to">{d.assigned_to_name ?? "—"}</Row>
            <Row label="Notes">{d.notes ?? "—"}</Row>
          </dl>
        </div>

        <div className="card lg:col-span-2">
          <h3 className="mb-3 font-medium">Assignment history</h3>
          {history.isLoading ? (
            <p className="text-sm text-slate-500">Loading history…</p>
          ) : (history.data ?? []).length === 0 ? (
            <p className="text-sm text-slate-500">This device has never been assigned.</p>
          ) : (
            <ol className="relative ml-3 space-y-6 border-l border-slate-200 pl-6 dark:border-slate-700">
              {history.data!.map((a) => (
                <li key={a.id} className="relative">
                  <span className="absolute -left-[33px] top-1 inline-flex h-3 w-3 rounded-full bg-brand-500" />
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div>
                      <div className="font-medium">{a.employee_name ?? "Unknown"}</div>
                      <div className="text-xs text-slate-500">
                        {new Date(a.assigned_at).toLocaleDateString()}{" "}
                        {a.returned_at
                          ? `→ ${new Date(a.returned_at).toLocaleDateString()}`
                          : "→ active"}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      {a.is_active ? (
                        <Badge status="assigned">active</Badge>
                      ) : (
                        <Badge>returned</Badge>
                      )}
                      {a.is_active ? (
                        <Button
                          variant="secondary"
                          onClick={() => returnAssignment.mutate(a.id)}
                          disabled={returnAssignment.isPending}
                        >
                          Mark returned
                        </Button>
                      ) : null}
                    </div>
                  </div>
                  {a.note ? (
                    <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{a.note}</p>
                  ) : null}
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-slate-500">{label}</dt>
      <dd className="text-right font-medium">{children}</dd>
    </div>
  );
}
