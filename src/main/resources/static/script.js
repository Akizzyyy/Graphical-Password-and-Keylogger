document.addEventListener("DOMContentLoaded", function () {
    const colors = ["red", "blue", "green", "yellow", "purple", "orange"];
    let selectedColors = [];

    function createGrid() {
        let grid = document.getElementById("colorGrid");
        colors.forEach(color => {
            let box = document.createElement("div");
            box.classList.add("color-box");
            box.style.backgroundColor = color;
            box.onclick = function () {
                if (selectedColors.includes(color)) {
                    selectedColors = selectedColors.filter(c => c !== color);
                    box.classList.remove("selected");
                } else if (selectedColors.length < 4) {
                    selectedColors.push(color);
                    box.classList.add("selected");
                }
            };
            grid.appendChild(box);
        });
    }

    createGrid();

    // Toggle between password and graphical password sections
    document.querySelectorAll("input[name='registerType']").forEach(radio => {
        radio.addEventListener("change", function () {
            if (this.value === "text") {
                document.getElementById("passwordSection").classList.remove("hidden");
                document.getElementById("graphicalPasswordSection").classList.add("hidden");
            } else {
                document.getElementById("passwordSection").classList.add("hidden");
                document.getElementById("graphicalPasswordSection").classList.remove("hidden");
            }
        });
    });

    document.getElementById("registerForm").addEventListener("submit", function (event) {
        event.preventDefault();

        let username = document.getElementById("registerUsername").value;
        let password = document.getElementById("registerPassword").value;
        let registerType = document.querySelector("input[name='registerType']:checked").value;

        if (registerType === "text" && password === "") {
            alert("Please enter a password.");
            return;
        }

        if (registerType === "graphical" && selectedColors.length !== 4) {
            alert("Please select exactly 4 colors for your graphical password.");
            return;
        }

        let userData = {
            username: username,
            password: registerType === "text" ? password : null,
            graphicalPassword: registerType === "graphical" ? selectedColors : null
        };

        localStorage.setItem(username, JSON.stringify(userData));
        document.getElementById("register-message").innerText = "Registration successful!";
        document.getElementById("register-message").style.display = "block";

        setTimeout(() => {
            window.location.href = "login.html";
        }, 1500);
    });
});
