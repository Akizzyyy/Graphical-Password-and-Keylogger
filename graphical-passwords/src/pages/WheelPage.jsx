import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ColorWheel from "../components/ColorWheel.jsx";
import "./WheelPage.css";

// Helper function to shuffle arrays
function shuffle(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

export default function WheelPage() {
    const [username, setUsername] = useState("");
    const [selectedColors, setSelectedColors] = useState(["", "", ""]);
    const [rotations, setRotations] = useState([0, 0, 0]);
    const [colorIndices, setColorIndices] = useState([0, 0, 0]);
    const [showModal, setShowModal] = useState(false);
    const [mode, setMode] = useState("login");

    const [wheel1Colors, setWheel1Colors] = useState([]);
    const [wheel2Colors, setWheel2Colors] = useState([]);
    const [wheel3Colors, setWheel3Colors] = useState([]);

    const navigate = useNavigate();

    useEffect(() => {
        setWheel1Colors(shuffle(["red", "green", "blue", "yellow", "purple", "orange"]));
        setWheel2Colors(shuffle(["cyan", "magenta", "lime", "pink", "gray", "brown"]));
        setWheel3Colors(shuffle(["gold", "silver", "navy", "teal", "maroon", "olive"]));
    }, []);

    const wheels = [wheel1Colors, wheel2Colors, wheel3Colors];

    const spinToColor = (index) => {
        const colors = wheels[index];
        const currentIdx = colorIndices[index];
        const nextIdx = (currentIdx + 1) % colors.length;
        const nextColor = colors[nextIdx];

        const degreesPerColor = 360 / colors.length;
        const finalRotation = 360 * 3 - (nextIdx * degreesPerColor);

        setColorIndices((prev) => {
            const updated = [...prev];
            updated[index] = nextIdx;
            return updated;
        });

        setRotations((prev) => {
            const updated = [...prev];
            updated[index] = finalRotation;
            return updated;
        });

        setSelectedColors((prev) => {
            const updated = [...prev];
            updated[index] = nextColor;
            return updated;
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!username || selectedColors.includes("")) {
            alert("Please enter your username and spin all wheels.");
            return;
        }

        const endpoint = mode === "login" ? "/auth" : "/register";

        try {
            const response = await fetch(`http://localhost:5000${endpoint}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    username,
                    method: "spinning-wheel",
                    passwordData: selectedColors,
                    wheelOrder: [wheel1Colors, wheel2Colors, wheel3Colors],
                }),
            });

            const data = await response.json();

            if (response.ok) {
                setShowModal(true);
            } else {
                alert(data.message || `${mode === "login" ? "Login" : "Registration"} failed.`);
            }
        } catch (error) {
            console.error(`${mode} error:`, error);
            alert(`${mode === "login" ? "Login" : "Registration"} failed. Please try again.`);
        }
    };

    const toggleMode = () => {
        setMode((prev) => (prev === "login" ? "register" : "login"));
        setUsername("");
        setSelectedColors(["", "", ""]);
        setRotations([0, 0, 0]);
        setColorIndices([0, 0, 0]);
        setShowModal(false);
        setWheel1Colors(shuffle(["red", "green", "blue", "yellow", "purple", "orange"]));
        setWheel2Colors(shuffle(["cyan", "magenta", "lime", "pink", "gray", "brown"]));
        setWheel3Colors(shuffle(["gold", "silver", "navy", "teal", "maroon", "olive"]));
    };

    return (
        <div className="auth-container">
            <div className="wheel-wrapper">
                <h2>{mode === "login" ? "Login" : "Create Account"}</h2>

                <input
                    type="text"
                    className="auth-input"
                    placeholder="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />

                {mode === "register" && (
                    <div className="selected-colors">
                        {selectedColors.map((color, index) => (
                            <div
                                key={index}
                                className="color-display"
                                style={{ backgroundColor: color || "lightgray" }}
                                title={color || "Not selected"}
                            ></div>
                        ))}
                    </div>
                )}

                <div className="wheel-container">
                    <div className="arrow-indicator bottom-right">▶</div>
                    {wheels.map((colors, index) => (
                        <div
                            key={index}
                            className="wheel"
                            style={{
                                width: `${400 - index * 100}px`,
                                height: `${400 - index * 100}px`,
                                position: "absolute",
                                top: "50%",
                                left: "50%",
                                transform: "translate(-50%, -50%)",
                            }}
                        >
                            <ColorWheel
                                colors={colors}
                                size={`${400 - index * 100}px`}
                                rotation={rotations[index]}
                                onClick={() => spinToColor(index)}
                            />
                        </div>
                    ))}
                </div>

                <button onClick={handleSubmit} className="register-btn">
                    {mode === "login" ? "Login" : "Register"}
                </button>

                <button onClick={toggleMode} className="toggle-btn">
                    Switch to {mode === "login" ? "Register" : "Login"}
                </button>

                <button
                    className="toggle-btn"
                    onClick={() => navigate("/")}
                    style={{ marginTop: "10px" }}
                >
                    ← Back to Dashboard
                </button>
            </div>

            {showModal && (
                <div className="modal-backdrop">
                    <div className="modal">
                        <h3>{mode === "login" ? "Login" : "Registration"} Successful</h3>
                        <p>Return to home page?</p>
                        <div className="modal-buttons">
                            <button className="confirm-btn" onClick={() => navigate("/")}>
                                Yes
                            </button>
                            <button className="cancel-btn" onClick={() => setShowModal(false)}>
                                No
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
