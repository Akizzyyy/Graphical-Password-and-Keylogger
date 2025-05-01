const { spawn } = require("child_process");

let serverProcess;

beforeAll((done) => {
    serverProcess = spawn("node", ["server.js"], {
        stdio: "inherit",
        shell: true,
    });

    // Wait a moment for the server to be ready
    setTimeout(done, 1500);
});

afterAll((done) => {
    if (serverProcess) {
        serverProcess.kill("SIGTERM");
    }

    setTimeout(() => {
        done();
    }, 500); // Ensure all async ops finish
});
