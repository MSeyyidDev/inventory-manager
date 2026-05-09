import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Pagination } from "../Pagination";

describe("Pagination", () => {
  it("displays the current range", () => {
    render(<Pagination page={2} pageSize={10} total={45} onPageChange={() => {}} />);
    expect(screen.getByText(/11–20 of 45/)).toBeInTheDocument();
  });

  it("invokes onPageChange when next is clicked", async () => {
    const onPageChange = vi.fn();
    render(
      <Pagination page={1} pageSize={10} total={50} onPageChange={onPageChange} />
    );
    await userEvent.click(screen.getByRole("button", { name: /next/i }));
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  it("disables previous on the first page", () => {
    render(<Pagination page={1} pageSize={10} total={50} onPageChange={() => {}} />);
    expect(screen.getByRole("button", { name: /previous/i })).toBeDisabled();
  });
});
