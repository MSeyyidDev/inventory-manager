import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Badge } from "../Badge";

describe("Badge", () => {
  it("renders text", () => {
    render(<Badge>hello</Badge>);
    expect(screen.getByText("hello")).toBeInTheDocument();
  });

  it("uses status color when status is provided", () => {
    render(<Badge status="available">free</Badge>);
    const el = screen.getByText("free");
    expect(el.className).toMatch(/emerald/);
  });
});
