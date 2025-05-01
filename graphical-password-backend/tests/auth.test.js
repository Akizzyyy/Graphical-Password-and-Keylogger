const request = require("supertest");

describe("POST /auth", () => {
    const baseURL = "http://localhost:5000";

    it("should return 404 if user not found", async () => {
        const res = await request(baseURL).post("/auth").send({
            username: "unknownuser",
            method: "emoji-grid",
            passwordData: ["😀"],
            grid: new Array(25).fill("😀")
        });
        expect(res.statusCode).toBe(404);
        expect(res.body.message).toBe("User not found for this method");
    });
});
