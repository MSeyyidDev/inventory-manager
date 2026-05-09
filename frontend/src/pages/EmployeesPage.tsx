import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "@/components/PageHeader";
import { DataTable, Column } from "@/components/DataTable";
import { Pagination } from "@/components/Pagination";
import { useEmployees } from "@/features/employees/useEmployees";
import type { Employee } from "@/api/types";

const PAGE_SIZE = 25;

export function EmployeesPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const employees = useEmployees({ page, page_size: PAGE_SIZE, search: search || undefined });

  const columns: Column<Employee>[] = [
    { key: "id", header: "ID", render: (e) => e.id, className: "w-16" },
    { key: "name", header: "Name", render: (e) => e.full_name },
    {
      key: "email",
      header: "Email",
      render: (e) => <span className="font-mono text-xs">{e.email}</span>,
    },
    { key: "department", header: "Department", render: (e) => e.department },
    { key: "role", header: "Role", render: (e) => e.role },
  ];

  return (
    <div>
      <PageHeader
        title="Employees"
        subtitle="Browse staff members and the devices they currently hold."
      />
      <div className="card mb-4">
        <input
          className="input"
          placeholder="Search by name or email…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
      </div>
      <DataTable<Employee>
        columns={columns}
        rows={employees.data?.items ?? []}
        rowKey={(e) => e.id}
        loading={employees.isLoading}
        onRowClick={(e) => navigate(`/employees/${e.id}`)}
      />
      <div className="mt-4">
        <Pagination
          page={page}
          pageSize={PAGE_SIZE}
          total={employees.data?.total ?? 0}
          onPageChange={setPage}
        />
      </div>
    </div>
  );
}
