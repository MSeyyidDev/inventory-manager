import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Modal } from "@/components/Modal";
import { Button } from "@/components/Button";
import { Select } from "@/components/Select";
import { assignmentsApi } from "@/api/assignmentsApi";
import { useEmployees } from "@/features/employees/useEmployees";
import type { Device } from "@/api/types";

interface AssignDeviceModalProps {
  device: Device | null;
  open: boolean;
  onClose: () => void;
}

export function AssignDeviceModal({ device, open, onClose }: AssignDeviceModalProps) {
  const queryClient = useQueryClient();
  const employees = useEmployees({ page: 1, page_size: 200 });
  const [employeeId, setEmployeeId] = useState<string>("");
  const [note, setNote] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const assign = useMutation({
    mutationFn: () =>
      assignmentsApi.assign({
        device_id: device!.id,
        employee_id: Number(employeeId),
        note: note || undefined,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["devices"] });
      queryClient.invalidateQueries({ queryKey: ["device", device?.id] });
      queryClient.invalidateQueries({ queryKey: ["stats-overview"] });
      setEmployeeId("");
      setNote("");
      onClose();
    },
    onError: (err: Error) => setError(err.message),
  });

  const options = useMemo(
    () =>
      (employees.data?.items ?? []).map((e) => ({
        value: String(e.id),
        label: `${e.full_name} (${e.department})`,
      })),
    [employees.data]
  );

  return (
    <Modal
      open={open}
      onClose={onClose}
      title={device ? `Assign ${device.manufacturer} ${device.model}` : "Assign device"}
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={() => assign.mutate()} disabled={!employeeId || assign.isPending}>
            {assign.isPending ? "Assigning…" : "Assign"}
          </Button>
        </>
      }
    >
      <div className="flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-slate-700 dark:text-slate-300">Employee</span>
          <Select
            value={employeeId}
            options={options}
            placeholder="Select an employee…"
            onChange={(e) => setEmployeeId(e.target.value)}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-slate-700 dark:text-slate-300">Note (optional)</span>
          <textarea
            className="input min-h-[80px] py-2"
            value={note}
            onChange={(e) => setNote(e.target.value)}
          />
        </label>
        {error ? <p className="text-sm text-red-600">{error}</p> : null}
      </div>
    </Modal>
  );
}
