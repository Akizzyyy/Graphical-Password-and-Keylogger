const express = require("express");
const bcrypt = require("bcryptjs");
const User = require("../models/User"); // assuming you have a User model
const router = express.Router();

// POST /auth/register - Handle registration
router.post("/register", async (req, res) => {
    const { username, password, pattern } = req.body;

    if (!username || !password || !pattern) {
        return res.status(400).json({ message: "All fields are required" });
    }

    try {
        // Check if user exists
        const userExists = await User.findOne({ username });
        if (userExists) {
            return res.status(400).json({ message: "User already exists" });
        }

        // Hash password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // Create new user
        const newUser = new User({ username, password: hashedPassword, pattern });
        await newUser.save();

        res.status(201).json({ message: "User created successfully" });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Server error" });
    }
});

// POST /auth/login - Handle login
router.post("/login", async (req, res) => {
    const { username, password, pattern } = req.body;

    if (!username || !password || !pattern) {
        return res.status(400).json({ message: "All fields are required" });
    }

    try {
        // Check if user exists
        const user = await User.findOne({ username });
        if (!user) {
            return res.status(400).json({ message: "Invalid credentials" });
        }

        // Compare password
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ message: "Invalid credentials" });
        }

        // Optionally, check the pattern here if needed for graphical password validation

        res.json({ message: "Login successful", success: true });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Server error" });
    }
});

module.exports = router;
