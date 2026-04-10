const API = "http://localhost:5000/api";

async function loadPatients() {
    const res = await fetch(`${API}/patients`, { credentials: "include" });

    if (res.status === 401) {
        window.location.href = "index.html";   // not logged in → back to login
        return;
    }

    const patients = await res.json();
    const grid     = document.getElementById("doctorGrid");

    patients.forEach(p => {
        const card = document.createElement("div");
        card.className = "patient-card clickable";
        card.innerHTML = `
            <img src="${p.img}" />
            <h3><i class="fa-solid fa-user"></i> ${p.name}</h3>
            <p><i class="fa-solid fa-calendar"></i> Age: ${p.age}</p>
            <p><i class="fa-solid fa-cake-candles"></i> DOB: ${p.dob}</p>
            <p><i class="fa-solid fa-venus-mars"></i> Gender: ${p.gender}</p>
        `;
        card.onclick = () => window.location.href = `patientDetails.html?id=${p.id}`;
        grid.appendChild(card);
    });
}

loadPatients();
