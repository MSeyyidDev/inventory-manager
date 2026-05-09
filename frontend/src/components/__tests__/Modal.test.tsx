import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { Modal } from "../Modal";

describe("Modal", () => {
  it("does not render when closed", () => {
    render(
      <Modal open={false} onClose={() => {}} title="Hidden">
        body
      </Modal>
    );
    expect(screen.queryByText(/hidden/i)).not.toBeInTheDocument();
  });

  it("renders title and body when open", () => {
    render(
      <Modal open onClose={() => {}} title="Visible">
        Body content
      </Modal>
    );
    expect(screen.getByText(/visible/i)).toBeInTheDocument();
    expect(screen.getByText(/body content/i)).toBeInTheDocument();
  });

  it("invokes onClose when the close button is pressed", async () => {
    const onClose = vi.fn();
    render(
      <Modal open onClose={onClose} title="Closable">
        body
      </Modal>
    );
    await userEvent.click(screen.getByLabelText(/close/i));
    expect(onClose).toHaveBeenCalledOnce();
  });
});
