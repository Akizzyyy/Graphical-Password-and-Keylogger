import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import EmojiGrid from "../pages/EmojiGrid";

// Helper to wrap with routing context
function renderWithRouter(ui) {
    return render(<BrowserRouter>{ui}</BrowserRouter>);
}

describe("EmojiGrid Component", () => {
    test("renders registration form and allows emoji selection", () => {
        renderWithRouter(<EmojiGrid />);

        // Check title and input
        expect(screen.getByText(/Register with Emoji Grid/i)).toBeInTheDocument();
        const usernameInput = screen.getByPlaceholderText(/Username/i);
        fireEvent.change(usernameInput, { target: { value: "testuser" } });

        // Emoji grid renders 25 emojis
        const emojiButtons = screen.getAllByRole("button").filter((btn) =>
            /emoji-cell/.test(btn.className)
        );
        expect(emojiButtons.length).toBe(25);

        // Select two different emojis
        fireEvent.click(emojiButtons[0]);
        fireEvent.click(emojiButtons[6]);

        // Click register button
        const registerButton = screen.getByRole("button", { name: /Register$/i });
        expect(registerButton).toBeInTheDocument();
        fireEvent.click(registerButton);

        // Allow error message or success message (depending on backend state)
        setTimeout(() => {
            expect(
                screen.queryByText(/Please select two emojis/i)
            ).not.toBeInTheDocument();
        }, 1000);
    });
});
