import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PageHeader } from "@/components/PageHeader";
import { KpiCard } from "@/components/KpiCard";
import { useStats } from "@/features/dashboard/useStats";

const PIE_COLORS = ["#3e54d6", "#7892fa", "#5670ee", "#9fb4ff", "#212c6e"];

export function DashboardPage() {
  const { data, isLoading, error } = useStats();

  return (
    <div>
      <PageHeader
        title="Dashboard"
        subtitle="Real-time overview of your IT asset inventory."
      />

      {error ? (
        <div className="card border-red-200 text-red-700">Failed to load stats: {error.message}</div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard label="Devices" value={isLoading ? "…" : data?.total_devices ?? 0} />
        <KpiCard label="Employees" value={isLoading ? "…" : data?.total_employees ?? 0} />
        <KpiCard label="Locations" value={isLoading ? "…" : data?.total_locations ?? 0} />
        <KpiCard
          label="Active assignments"
          value={isLoading ? "…" : data?.active_assignments ?? 0}
          hint="Currently with an employee"
        />
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="card h-80">
          <h3 className="mb-2 font-medium">Devices by type</h3>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={data?.devices_by_type ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
              <XAxis dataKey="key" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#3e54d6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="card h-80">
          <h3 className="mb-2 font-medium">Devices by status</h3>
          <ResponsiveContainer width="100%" height="90%">
            <PieChart>
              <Pie
                data={data?.devices_by_status ?? []}
                dataKey="count"
                nameKey="key"
                outerRadius={90}
                label
              >
                {(data?.devices_by_status ?? []).map((_, idx) => (
                  <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Legend />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card h-80 lg:col-span-2">
          <h3 className="mb-2 font-medium">Devices by location</h3>
          <ResponsiveContainer width="100%" height="90%">
            <BarChart data={data?.devices_by_location ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
              <XAxis dataKey="key" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#7892fa" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
