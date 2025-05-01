import React from "react";
import { render, fireEvent } from "@testing-library/react";
import ColorWheel from "../components/ColorWheel";

describe("ColorWheel Component", () => {
    const mockColors = ["red", "green", "blue", "yellow", "purple", "orange"];
    const mockClick = jest.fn();

    it("renders SVG with correct number of segments", () => {
        const { container } = render(
            <ColorWheel colors={mockColors} size="300px" onClick={mockClick} />
        );
        const segments = container.querySelectorAll("path");
        expect(segments.length).toBe(mockColors.length);
    });

    it("triggers onClick when a segment is clicked", () => {
        const { container } = render(
            <ColorWheel colors={mockColors} size="300px" onClick={mockClick} />
        );
        const segments = container.querySelectorAll("path");
        fireEvent.click(segments[0]);
        expect(mockClick).toHaveBeenCalled();
    });
});
