import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./EmojiGrid.css";

const EMOJIS = [
    "😀", "😎", "🐱", "🐶", "😡",
    "👽", "⛪", "🤖", "💩", "👻",
    "🦄", "🐸", "🐵", "🦊", "🐷",
    "🐼", "🐙", "🧠", "👁️", "👅",
    "🦷", "🧛", "🧟", "🦸", "🧞"
];

export default function EmojiGrid() {
    const [grid, setGrid] = useState([]);
    const [selected, setSelected] = useState([]);
    const [username, setUsername] = useState("");
    const [mode, setMode] = useState("register");
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const location = useLocation();
    const gridSize = 5;

    useEffect(() => {
        const params = new URLSearchParams(location.search);
        const urlMode = params.get("mode");
        if (urlMode === "login" || urlMode === "register") {
            setMode(urlMode);
        }
        setGrid(generateGrid());
        setSelected([]);
        setMessage("");
        setError("");
    }, [location.search]);

    const generateGrid = () => {
        const shuffled = [...EMOJIS].sort(() => Math.random() - 0.5);
        return Array.from({ length: gridSize }, (_, i) =>
            shuffled.slice(i * gridSize, i * gridSize + gridSize)
        );
    };

    const handleRefreshGrid = () => {
        setGrid(generateGrid());
        setSelected([]);
        setError("");
        setMessage("");
    };

    const handleSelect = (row, col) => {
        const emoji = grid[row][col];

        if (mode === "login") {
            setSelected([{ emoji, row, col }]);
            return;
        }


        if (selected.find(s => s.emoji === emoji)) {
            setError("You already selected this emoji.");
            return;
        }

        if (selected.length === 0) {
            setSelected([{ emoji, row, col }]);
            setError("");
        } else if (selected.length === 1) {
            const first = selected[0];
            const isValid = first.row !== row && first.col !== col;
            if (!isValid) {
                setError("Pick emojis on different rows and columns.");
                return;
            }
            setSelected([...selected, { emoji, row, col }]);
            setError("");
        }
    };

    const isSelected = (row, col) => {
        const emoji = grid[row][col];
        return selected.some(sel =>
            sel.row === row && sel.col === col ||
            (mode === "login" && selected.length && sel.emoji === emoji)
        );
    };

    const handleSubmit = async () => {
        if (!username) {
            setError("Please enter a username.");
            return;
        }

        if (mode === "register" && selected.length !== 2) {
            setError("Please select two emojis.");
            return;
        }

        if (mode === "login" && selected.length !== 1) {
            setError("Please select the intersection emoji.");
            return;
        }

        const payload = {
            username,
            method: "emoji-grid",
            passwordData: mode === "register"
                ? [selected[0].emoji, selected[1].emoji]
                : [selected[0].emoji],
            ...(mode === "login" && {
                clickedRow: selected[0].row,
                clickedCol: selected[0].col,
                grid: grid.flat()
            })
        };


        if (mode === "login") {
            payload.grid = grid.flat();
        }

        try {
            const response = await fetch(`http://localhost:5000/${mode === "register" ? "register" : "auth"}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (response.ok) {
                setMessage(data.message);
                setError("");

                if (mode === "register") {
                    setTimeout(() => {
                        navigate("/emoji-auth?mode=login");
                    }, 1500);
                } else {
                    setTimeout(() => navigate("/"), 1500);
                }
            } else {
                setError(data.message || "Something went wrong.");
                setMessage("");
            }
        } catch (err) {
            console.error("Server error:", err);
            setError("Server error. Try again.");
            setMessage("");
        }
    };

    return (
        <div className="emoji-grid-wrapper">
            <h2>{mode === "register" ? "Register with Emoji Grid" : "Login with Emoji Grid"}</h2>

            <input
                className="auth-input"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />

            <div className="emoji-grid">
                {grid.map((row, rIdx) =>
                    row.map((emoji, cIdx) => (
                        <button
                            key={`${rIdx}-${cIdx}`}
                            className={`emoji-cell ${isSelected(rIdx, cIdx) ? "selected" : ""}`}
                            onClick={() => handleSelect(rIdx, cIdx)}
                        >
                            {emoji}
                        </button>
                    ))
                )}
            </div>

            {mode === "login" && (
                <button className="refresh-btn" onClick={handleRefreshGrid}>
                    🔄 Refresh Grid
                </button>
            )}

            <button className="auth-btn" onClick={handleSubmit}>
                {mode === "register" ? "Register" : "Login"}
            </button>

            <button className="toggle-btn" onClick={() => {
                const newMode = mode === "register" ? "login" : "register";
                navigate(`/emoji-auth?mode=${newMode}`);
            }}>
                {mode === "register" ? "Already registered? Log in" : "New user? Register here"}
            </button>


            <button
                className="toggle-btn"
                onClick={() => navigate("/")}
                style={{ marginTop: "10px" }}
            >
                ← Back to Dashboard
            </button>

            {error && <p className="error-text">{error}</p>}
            {message && <p className="success-text">{message}</p>}
        </div>
    );
}
