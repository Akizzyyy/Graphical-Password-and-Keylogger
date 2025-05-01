const mongoose = require("mongoose");

const UserSchema = new mongoose.Schema({
    username: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    pattern: { type: [String], required: true }, // Pattern can be an array of colors or numbers
});


const User = mongoose.models.User || mongoose.model("User", UserSchema);

module.exports = User;