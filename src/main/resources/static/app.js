async function submitForm() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const response = await fetch("http://localhost:8080/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, pattern: [1, 2, 3] }) // Example pattern
    });

    const result = await response.json();
    alert(result.message);

    if (result.success) {
        window.location.href = "dashboard.html";  // Redirect on success
    }
}
