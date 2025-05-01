import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import WheelPage from "../pages/WheelPage";

function renderWithRouter(ui) {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe("WheelPage Component", () => {
    it("renders the username input and register button", () => {
        renderWithRouter(<WheelPage />);
        expect(screen.getByPlaceholderText(/Username/i)).toBeInTheDocument();
        expect(screen.getByText(/Register/i)).toBeInTheDocument();
    });

    it("allows user to type a username", () => {
        renderWithRouter(<WheelPage />);
        const input = screen.getByPlaceholderText(/Username/i);
        fireEvent.change(input, { target: { value: "testuser" } });
        expect(input.value).toBe("testuser");
    });

    it("clicks the register button without crashing", () => {
        renderWithRouter(<WheelPage />);
        const button = screen.getByText(/Register/i);
        fireEvent.click(button);
        expect(button).toBeInTheDocument(); // Confirm button is interactable
    });

    it("toggles to login mode", () => {
        renderWithRouter(<WheelPage />);
        const toggleBtn = screen.getByText((content) => content.includes("Switch to"));
        fireEvent.click(toggleBtn);
        expect(screen.getByText(/Login/i)).toBeInTheDocument();
    });
});
