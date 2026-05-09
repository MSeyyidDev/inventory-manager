import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DataTable, Column } from "../DataTable";

interface Row {
  id: number;
  name: string;
}

const columns: Column<Row>[] = [
  { key: "id", header: "ID", render: (r) => r.id, sortable: true },
  { key: "name", header: "Name", render: (r) => r.name, sortable: true },
];

describe("DataTable", () => {
  it("renders rows", () => {
    render(
      <DataTable<Row>
        columns={columns}
        rows={[{ id: 1, name: "A" }]}
        rowKey={(r) => r.id}
      />
    );
    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("shows the empty placeholder when there are no rows", () => {
    render(
      <DataTable<Row>
        columns={columns}
        rows={[]}
        rowKey={(r) => r.id}
        empty="Nothing here"
      />
    );
    expect(screen.getByText(/nothing here/i)).toBeInTheDocument();
  });

  it("calls onSortChange when a sortable header is clicked", async () => {
    const onSortChange = vi.fn();
    render(
      <DataTable<Row>
        columns={columns}
        rows={[{ id: 1, name: "A" }]}
        rowKey={(r) => r.id}
        sortBy="id"
        sortDir="asc"
        onSortChange={onSortChange}
      />
    );
    await userEvent.click(screen.getByRole("button", { name: /name/i }));
    expect(onSortChange).toHaveBeenCalledWith("name");
  });
});
