import React from "react";
import { Link } from "react-router-dom";
import "./Dashboard.css";

export default function Dashboard() {
    return (
        <div className="dashboard-container">
            <div className="dashboard-card">
                <h1 className="dashboard-title">🔐 Graphical Authentication</h1>
                <p className="dashboard-subtitle">Choose a secure and visual way to log in.</p>

                <div className="auth-options">
                    <Link to="/wheel" className="auth-card">
                        <h3>🎡 Spinning Wheel Password</h3>
                        <p>Rotate and match your color combo to log in securely.</p>
                    </Link>

                    <Link to="/emoji-auth?mode=login" className="auth-card">
                        <h3>🔲 Emoji Grid Auth</h3>
                        <p>Register or log in using emoji grid intersection.</p>
                    </Link>

                </div>
            </div>
        </div>
    );
}
