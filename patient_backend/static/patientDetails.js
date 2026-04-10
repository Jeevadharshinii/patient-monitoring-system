const API = "http://localhost:5000/api";

const urlParams = new URLSearchParams(window.location.search);
const pid       = urlParams.get("id");

// ── Load patient basic info ──────────────────────────────────
async function loadPatient() {
    const res = await fetch(`${API}/patients/${pid}`, { credentials: "include" });

    if (res.status === 401) { window.location.href = "index.html"; return; }
    if (res.status === 403) { alert("Access denied"); history.back(); return; }

    const p = await res.json();

    document.getElementById("pImg").src               = p.img;
    document.getElementById("pName").textContent      = p.name;
    document.getElementById("pAge").textContent       = "Age: " + p.age;
    document.getElementById("pDob").textContent       = "DOB: " + p.dob;
    document.getElementById("pGender").textContent    = "Gender: " + p.gender;
    document.getElementById("pHR").textContent        = p.heart_rate;
    document.getElementById("pBP").textContent        = p.blood_pressure;
    document.getElementById("pOxy").textContent       = p.oxygen_level;
    document.getElementById("pTemp").textContent      = p.temperature;
    document.getElementById("pHistory").innerHTML     = p.history.map(h => `<li>${h}</li>`).join("");
}

// ── Load vitals history → render charts ─────────────────────
async function loadCharts() {
    const res  = await fetch(`${API}/patients/${pid}/vitals/history`, { credentials: "include" });
    const data = await res.json();

    renderChart("hrChart",   "Heart Rate (bpm)",   data.labels, data.heart_rate,   "rgb(239,68,68)");
    renderChart("bpChart",   "Systolic BP (mmHg)", data.labels, data.systolic_bp,  "rgb(59,130,246)");
    renderChart("oxyChart",  "Oxygen Level (%)",   data.labels, data.oxygen_level, "rgb(16,185,129)");
    renderChart("tempChart", "Temperature (°F)",   data.labels, data.temperature,  "rgb(245,158,11)");
}

function renderChart(canvasId, label, labels, values, color) {
    const ctx = document.getElementById(canvasId).getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels,
            datasets: [{
                label,
                data: values,
                borderColor:     color,
                backgroundColor: color.replace("rgb", "rgba").replace(")", ",0.15)"),
                borderWidth: 2,
                pointRadius: 4,
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: true } },
            scales:  { y: { beginAtZero: false } }
        }
    });
}

loadPatient();
loadCharts();
