const express = require("express");
const mongoose = require("mongoose");
const cors = require("cors");

const app = express();
app.use(express.json());
app.use(cors());

// === MongoDB Connection ===
mongoose.connect("mongodb://127.0.0.1:27017/graphical-auth")
    .then(() => console.log("✅ MongoDB connected"))
    .catch(err => console.error("❌ MongoDB connection error:", err));

// === Emoji Pool ===
const EMOJIS = [
    "😀", "😎", "🐱", "🐶", "😡",
    "👽", "⛪", "🤖", "💩", "👻",
    "🦄", "🐸", "🐵", "🦊", "🐷",
    "🐼", "🐙", "🧠", "👁️", "👅",
    "🦷", "🧛", "🧟", "🦸", "🧞"
];

// === User Schema ===
const UserSchema = new mongoose.Schema({
    username: { type: String, required: true },
    method: { type: String, required: true },
    passwordData: { type: Array, required: true },
    wheelOrder: { type: Array } // Store wheel order for spinning-wheel logins
});
UserSchema.index({ username: 1, method: 1 }, { unique: true });
const User = mongoose.model("User", UserSchema);

// === Register Endpoint ===
app.post("/register", async (req, res) => {
    const { username, method, passwordData, wheelOrder } = req.body;

    if (!username || !method || !Array.isArray(passwordData)) {
        return res.status(400).json({ message: "Invalid request format" });
    }

    try {
        const existingUser = await User.findOne({ username, method });
        if (existingUser) {
            return res.status(409).json({ message: "User already registered with this method" });
        }

        const user = new User({ username, method, passwordData, wheelOrder });
        await user.save();
        res.json({ message: "Registration successful" });
    } catch (error) {
        console.error("❌ Error registering user:", error);
        res.status(500).json({ message: "Server error during registration" });
    }
});

// === Auth Endpoint ===
app.post("/auth", async (req, res) => {
    const { username, method, passwordData, grid: submittedGrid, wheelOrder } = req.body;

    if (!username || !method || !Array.isArray(passwordData)) {
        return res.status(400).json({ message: "Invalid request format" });
    }

    try {
        const user = await User.findOne({ username, method });
        if (!user) {
            return res.status(404).json({ message: "User not found for this method" });
        }

        if (method === "spinning-wheel") {
            if (!Array.isArray(wheelOrder) || wheelOrder.length !== 3) {
                return res.status(400).json({ message: "Wheel order is missing or invalid" });
            }

            const expected = user.passwordData;
            const provided = passwordData;

            const match = expected.every((color, index) => wheelOrder[index].includes(color));

            if (match && JSON.stringify(expected) === JSON.stringify(provided)) {
                return res.json({ message: "Login successful" });
            } else {
                return res.status(401).json({ message: "Incorrect graphical password" });
            }
        }

        if (method === "emoji-grid") {
            if (!submittedGrid || submittedGrid.length !== 25) {
                return res.status(400).json({ message: "Missing emoji grid from client." });
            }

            const [emojiA, emojiB] = user.passwordData;
            const clickedEmoji = passwordData[0];

            const grid = Array.from({ length: 5 }, (_, i) =>
                submittedGrid.slice(i * 5, i * 5 + 5)
            );

            let rowA = null, colA = null, rowB = null, colB = null;

            for (let r = 0; r < 5; r++) {
                for (let c = 0; c < 5; c++) {
                    if (grid[r][c] === emojiA) {
                        rowA = r;
                        colA = c;
                    }
                    if (grid[r][c] === emojiB) {
                        rowB = r;
                        colB = c;
                    }
                }
            }


            console.log("🔍 Login attempt for:", username);
            console.table(grid);
            console.log("Emoji A:", emojiA, "at row", rowA);
            console.log("Emoji B:", emojiB, "at col", colB);
            console.log("User clicked:", clickedEmoji);

            if (rowA === null || colB === null) {
                return res.status(401).json({ message: "Registered emojis not found in grid." });
            }

            const expected1 = grid[rowA][colB];
            const expected2 = grid[rowB][colA];
            // === EXPORT OBSERVATION FOR SHOULDER SURFER AI ===
            const fs = require("fs");
            const aiLog = {
                timestamp: new Date().toISOString(),
                username,
                grid,
                clickedEmoji,
                row: rowA,
                col: colB,
                rowEmojis: grid[rowA],
                colEmojis: grid.map(row => row[colB])
            };

            fs.writeFileSync(
                `./observations/${username}_emoji_login.json`,
                JSON.stringify(aiLog, null, 2)
            );


            if (clickedEmoji === expected1 || clickedEmoji === expected2) {
                return res.json({ message: "Login successful" });
            } else {
                return res.status(401).json({ message: "Incorrect emoji grid password" });
            }

        }

        res.status(400).json({ message: "Unknown authentication method" });
    } catch (error) {
        console.error("❌ Authentication error:", error);
        res.status(500).json({ message: "Server error during authentication" });
    }
});

// === Start Server ===
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`🚀 Server running on port ${PORT}`));