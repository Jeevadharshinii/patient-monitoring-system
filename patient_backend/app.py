from flask import Flask, request, jsonify, session
from flask_cors import CORS
from database import init_db, get_db
from alerts import check_vitals, send_alert_email
import hashlib
import os

app = Flask(__name__)
app.secret_key = "patient_app_secret_key_2024"
CORS(app, supports_credentials=True)

with app.app_context():
    init_db()


def hash_password(pw): return hashlib.sha256(pw.encode()).hexdigest()

def login_required(role=None):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                return jsonify({"error": "Unauthorized"}), 401
            if role and session.get("role") != role:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator


# SERVE FRONTEND
@app.route("/")
def index(): return app.send_static_file("index.html")

@app.route("/doctorDashboard.html")
def doctor_dashboard(): return app.send_static_file("doctorDashboard.html")

@app.route("/caretakerDashboard.html")
def caretaker_dashboard(): return app.send_static_file("caretakerDashboard.html")

@app.route("/patientDetails.html")
def patient_details(): return app.send_static_file("patientDetails.html")


# AUTH
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role     = data.get("role", "").strip()
    if not username or not password or not role:
        return jsonify({"error": "All fields required"}), 400
    db   = get_db()
    user = db.execute("SELECT * FROM users WHERE username=? AND role=?", (username, role)).fetchone()
    if not user or user["password_hash"] != hash_password(password):
        return jsonify({"error": "Invalid credentials"}), 401
    session["user_id"]  = user["id"]
    session["role"]     = user["role"]
    session["username"] = user["username"]
    return jsonify({"message": "Login successful", "role": user["role"], "username": user["username"]})

@app.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})

@app.route("/api/me")
def me():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return jsonify({"user_id": session["user_id"], "role": session["role"], "username": session["username"]})


# DOCTOR
@app.route("/api/patients")
@login_required(role="doctor")
def get_all_patients():
    db = get_db()
    return jsonify([dict(p) for p in db.execute("SELECT * FROM patients").fetchall()])

@app.route("/api/patients/<int:pid>")
@login_required()
def get_patient(pid):
    db = get_db()
    if session["role"] == "caretaker":
        assigned = [r["patient_id"] for r in db.execute("SELECT patient_id FROM caretaker_patients WHERE user_id=?", (session["user_id"],)).fetchall()]
        if pid not in assigned:
            return jsonify({"error": "Forbidden"}), 403
    patient = db.execute("SELECT * FROM patients WHERE id=?", (pid,)).fetchone()
    if not patient:
        return jsonify({"error": "Not found"}), 404
    history = db.execute("SELECT note FROM medical_history WHERE patient_id=? ORDER BY created_at DESC", (pid,)).fetchall()
    result = dict(patient)
    result["history"] = [h["note"] for h in history]
    return jsonify(result)


# CARETAKER
@app.route("/api/caretaker/patients")
@login_required(role="caretaker")
def get_caretaker_patients():
    db = get_db()
    rows = db.execute(
        "SELECT p.* FROM patients p JOIN caretaker_patients cp ON p.id=cp.patient_id WHERE cp.user_id=?",
        (session["user_id"],)
    ).fetchall()
    return jsonify([dict(r) for r in rows])


# GRAPHS
@app.route("/api/patients/<int:pid>/vitals/history")
@login_required()
def vitals_history(pid):
    db = get_db()
    if session["role"] == "caretaker":
        assigned = [r["patient_id"] for r in db.execute("SELECT patient_id FROM caretaker_patients WHERE user_id=?", (session["user_id"],)).fetchall()]
        if pid not in assigned:
            return jsonify({"error": "Forbidden"}), 403
    rows = db.execute(
        "SELECT recorded_date, heart_rate, systolic_bp, diastolic_bp, oxygen_level, temperature FROM vitals_history WHERE patient_id=? ORDER BY recorded_date ASC LIMIT 7",
        (pid,)
    ).fetchall()
    return jsonify({
        "labels":       [r["recorded_date"] for r in rows],
        "heart_rate":   [r["heart_rate"]    for r in rows],
        "systolic_bp":  [r["systolic_bp"]   for r in rows],
        "diastolic_bp": [r["diastolic_bp"]  for r in rows],
        "oxygen_level": [r["oxygen_level"]  for r in rows],
        "temperature":  [r["temperature"]   for r in rows],
    })


# ADD VITALS + EMAIL ALERT
@app.route("/api/patients/<int:pid>/vitals", methods=["POST"])
@login_required(role="doctor")
def add_vitals(pid):
    data = request.get_json()
    db   = get_db()

    # Save to DB
    db.execute(
        "INSERT INTO vitals_history (patient_id, recorded_date, heart_rate, systolic_bp, diastolic_bp, oxygen_level, temperature) VALUES (?, date('now'), ?, ?, ?, ?, ?)",
        (pid, data["heart_rate"], data["systolic_bp"], data["diastolic_bp"], data["oxygen_level"], data["temperature"])
    )
    db.execute(
        "UPDATE patients SET heart_rate=?, blood_pressure=?, oxygen_level=?, temperature=? WHERE id=?",
        (f'{data["heart_rate"]} bpm', f'{data["systolic_bp"]}/{data["diastolic_bp"]} mmHg', f'{data["oxygen_level"]}%', f'{data["temperature"]}°F', pid)
    )
    db.commit()

    # Check vitals → send email if abnormal
    alerts = check_vitals(data)
    if alerts:
        patient = db.execute("SELECT name FROM patients WHERE id=?", (pid,)).fetchone()
        # Get caretaker email assigned to this patient
        caretakers = db.execute(
            "SELECT u.email FROM users u JOIN caretaker_patients cp ON u.id=cp.user_id WHERE cp.patient_id=?",
            (pid,)
        ).fetchall()
        for ct in caretakers:
            if ct["email"]:
                send_alert_email(ct["email"], patient["name"], data, alerts)

    return jsonify({
        "message": "Vitals updated",
        "alerts":  alerts,
        "alert_sent": len(alerts) > 0
    })


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
