const request = require("supertest");

describe("POST /register", () => {
    const baseURL = "http://localhost:5000";

    it("should register a new user", async () => {
        const res = await request(baseURL).post("/register").send({
            username: "user" + Date.now(),
            method: "emoji-grid",
            passwordData: ["😀", "😎"],
            wheelOrder: []
        });
        expect(res.statusCode).toBe(200);
        expect(res.body.message).toBe("Registration successful");
    });

    it("should reject duplicate registration", async () => {
        const userData = {
            username: "duplicateUser" + Date.now(),
            method: "emoji-grid",
            passwordData: ["😀", "😎"],
            wheelOrder: []
        };

        await request(baseURL).post("/register").send(userData);
        const res = await request(baseURL).post("/register").send(userData);
        expect(res.statusCode).toBe(409);
        expect(res.body.message).toBe("User already registered with this method");
    });
});
