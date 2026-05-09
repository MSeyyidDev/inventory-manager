import { Link, useParams } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { Badge } from "@/components/Badge";
import { useEmployee, useEmployeeDevices } from "@/features/employees/useEmployees";

export function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const numericId = id ? Number(id) : undefined;
  const employee = useEmployee(numericId);
  const devices = useEmployeeDevices(numericId);

  if (employee.isLoading) return <div>Loading…</div>;
  if (!employee.data) return <div>Not found.</div>;

  const e = employee.data;

  return (
    <div>
      <PageHeader
        title={e.full_name}
        subtitle={`${e.role} · ${e.department}`}
        actions={
          <Link to="/employees" className="btn-secondary">
            Back to employees
          </Link>
        }
      />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="card lg:col-span-1">
          <h3 className="mb-3 font-medium">Profile</h3>
          <dl className="space-y-2 text-sm">
            <div className="flex justify-between">
              <dt className="text-slate-500">Email</dt>
              <dd className="font-mono text-xs">{e.email}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Department</dt>
              <dd>{e.department}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-slate-500">Role</dt>
              <dd>{e.role}</dd>
            </div>
          </dl>
        </div>
        <div className="card lg:col-span-2">
          <h3 className="mb-3 font-medium">Currently assigned devices</h3>
          {devices.isLoading ? (
            <p className="text-sm text-slate-500">Loading…</p>
          ) : (devices.data ?? []).length === 0 ? (
            <p className="text-sm text-slate-500">No active assignments.</p>
          ) : (
            <ul className="divide-y divide-slate-100 dark:divide-slate-800">
              {devices.data!.map((a) => (
                <li key={a.id} className="flex items-center justify-between py-3">
                  <div>
                    <Link
                      to={`/devices/${a.device_id}`}
                      className="font-medium text-brand-600 hover:underline"
                    >
                      Device #{a.device_id}
                    </Link>
                    <div className="text-xs text-slate-500">
                      Assigned {new Date(a.assigned_at).toLocaleDateString()}
                    </div>
                  </div>
                  <Badge status="assigned">active</Badge>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
