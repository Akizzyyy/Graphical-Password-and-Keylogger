module.exports = {
    testEnvironment: "node",
    setupFilesAfterEnv: ["<rootDir>/tests/setup.js"],
    transform: {},
    forceExit: true, // <-- Add this
    detectOpenHandles: true // Optional for debugging
};
