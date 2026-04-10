// ─── CONFIG ─────────────────────────────────────────────────
const API = "http://localhost:5000/api";   // Change to your Antigravity URL

// ─── ROLE TOGGLE ────────────────────────────────────────────
let selectedRole = "doctor";

function selectRole(role) {
    selectedRole = role;
    document.getElementById("doctorBtn").classList.toggle("active",    role === "doctor");
    document.getElementById("caretakerBtn").classList.toggle("active", role === "caretaker");
}

// ─── LOGIN ──────────────────────────────────────────────────
async function login() {
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const error    = document.getElementById("error");
    error.textContent = "";

    if (!username || !password) {
        error.textContent = "Please fill all fields!";
        return;
    }

    try {
        const res = await fetch(`${API}/login`, {
            method:      "POST",
            credentials: "include",          // send session cookie
            headers:     { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password, role: selectedRole })
        });

        const data = await res.json();

        if (!res.ok) {
            error.textContent = data.error || "Login failed";
            return;
        }

        // Redirect based on role
        if (data.role === "doctor") {
            window.location.href = "doctorDashboard.html";
        } else {
            window.location.href = "caretakerDashboard.html";
        }

    } catch (err) {
        error.textContent = "Cannot reach server. Is Flask running?";
    }
}

// ─── SHOW / HIDE PASSWORD ───────────────────────────────────
document.getElementById("togglePassword").addEventListener("click", () => {
    const pw   = document.getElementById("password");
    const icon = document.getElementById("togglePassword");
    pw.type    = pw.type === "password" ? "text" : "password";
    icon.textContent = pw.type === "password" ? "👁️" : "🙈";
});
