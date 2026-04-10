# Patient App – Backend Setup Guide

## Project Structure

```
patient_backend/
├── app.py           ← Flask app (all API routes)
├── database.py      ← SQLite setup + seed data
├── requirements.txt
├── db/
│   └── patient_app.db   ← auto-created on first run
└── static/              ← Updated frontend JS files
    ├── script.js         (login → calls /api/login)
    ├── doctor.js         (fetches all patients)
    ├── caretaker.js      (fetches assigned patients)
    ├── patientDetails.js (patient info + 4 health charts)
    └── patientDetails.html (updated – includes chart canvases)
```

---

## Step 1 – Install dependencies

```bash
pip install -r requirements.txt
```

---

## Step 2 – Run the Flask server

```bash
python app.py
```

Server starts at: `http://localhost:5000`  
First run automatically creates the SQLite DB and seeds data.

---

## Step 3 – Update frontend files

Copy these files from `static/` into your frontend folder (replacing the old ones):
- `script.js`
- `doctor.js`
- `caretaker.js`
- `patientDetails.js`
- `patientDetails.html`

Also **delete** `data.js` from the frontend (no longer needed – data comes from DB now).

Update the `API` constant at the top of each JS file to your Antigravity server URL:
```js
const API = "https://your-antigravity-url.com/api";
```

---

## API Endpoints

| Method | Endpoint                              | Access      | Description                     |
|--------|---------------------------------------|-------------|---------------------------------|
| POST   | `/api/login`                          | Public      | Login with username/password/role |
| POST   | `/api/logout`                         | Logged in   | Logout                          |
| GET    | `/api/me`                             | Logged in   | Current user info               |
| GET    | `/api/patients`                       | Doctor only | All patients list               |
| GET    | `/api/patients/<id>`                  | Doctor/Caretaker | Single patient + history   |
| GET    | `/api/caretaker/patients`             | Caretaker   | Assigned patients only          |
| GET    | `/api/patients/<id>/vitals/history`   | Doctor/Caretaker | 7-day vitals for graphs    |
| POST   | `/api/patients/<id>/vitals`           | Doctor only | Add new vitals reading          |

---

## Default Login Credentials

| Username | Password | Role       | Can See          |
|----------|----------|------------|------------------|
| doctor1  | doc123   | doctor     | All patients     |
| care1    | care123  | caretaker  | Patient 1 (John) |
| care2    | care456  | caretaker  | Patient 2 (Ram)  |

---

## Database Tables

- **users** – login credentials (passwords stored as SHA-256 hash)
- **patients** – patient profile + current vitals
- **medical_history** – history notes per patient
- **caretaker_patients** – which caretaker manages which patient
- **vitals_history** – 7-day vitals records (used for graphs)

---

## Health Report Graphs

When a doctor or caretaker opens a patient's detail page, 4 line charts are rendered using **Chart.js**:

1. 📈 Heart Rate (bpm) – last 7 days
2. 📈 Systolic Blood Pressure (mmHg) – last 7 days
3. 📈 Oxygen Level (%) – last 7 days
4. 📈 Temperature (°F) – last 7 days

Data comes from `GET /api/patients/<id>/vitals/history`
