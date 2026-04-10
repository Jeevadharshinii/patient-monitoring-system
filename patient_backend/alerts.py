import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Gmail config ──────────────────────────────────────────────
SENDER_EMAIL = "herejeevadharshini@gmail.com"
APP_PASSWORD  = "xyhd ysvz fgiu skar"

# ── Normal ranges ─────────────────────────────────────────────
NORMAL = {
    "heart_rate":  (60, 100),    # bpm
    "systolic_bp": (90, 130),    # mmHg
    "diastolic_bp":(60, 90),     # mmHg
    "oxygen_level":(95, 100),    # %
    "temperature": (97.0, 99.0), # °F
}

def check_vitals(vitals: dict) -> list:
    """Returns list of alert messages for abnormal vitals."""
    alerts = []
    checks = [
        ("heart_rate",   vitals.get("heart_rate"),   "Heart Rate",    "bpm"),
        ("systolic_bp",  vitals.get("systolic_bp"),  "Systolic BP",   "mmHg"),
        ("diastolic_bp", vitals.get("diastolic_bp"), "Diastolic BP",  "mmHg"),
        ("oxygen_level", vitals.get("oxygen_level"), "Oxygen Level",  "%"),
        ("temperature",  vitals.get("temperature"),  "Temperature",   "°F"),
    ]
    for key, value, label, unit in checks:
        if value is None:
            continue
        low, high = NORMAL[key]
        if value < low:
            alerts.append(f"⚠️ {label} is LOW: {value} {unit} (Normal: {low}–{high})")
        elif value > high:
            alerts.append(f"🚨 {label} is HIGH: {value} {unit} (Normal: {low}–{high})")
    return alerts


def send_alert_email(caretaker_email: str, patient_name: str, vitals: dict, alerts: list):
    """Sends alert email to caretaker if vitals are abnormal."""
    if not alerts:
        return  # Nothing to send

    subject = f"🚨 Health Alert: {patient_name} – Abnormal Vitals Detected"

    body = f"""
    <html><body>
    <h2 style="color:red;">⚠️ Health Alert for {patient_name}</h2>
    <p>The following abnormal vitals were recorded:</p>
    <ul>
        {''.join(f'<li style="color:darkred;"><b>{a}</b></li>' for a in alerts)}
    </ul>
    <hr>
    <h3>Full Vitals Reading:</h3>
    <table border="1" cellpadding="6" style="border-collapse:collapse;">
        <tr><th>Vital</th><th>Value</th><th>Normal Range</th></tr>
        <tr><td>Heart Rate</td><td>{vitals.get('heart_rate')} bpm</td><td>60–100 bpm</td></tr>
        <tr><td>Systolic BP</td><td>{vitals.get('systolic_bp')} mmHg</td><td>90–130 mmHg</td></tr>
        <tr><td>Diastolic BP</td><td>{vitals.get('diastolic_bp')} mmHg</td><td>60–90 mmHg</td></tr>
        <tr><td>Oxygen Level</td><td>{vitals.get('oxygen_level')}%</td><td>95–100%</td></tr>
        <tr><td>Temperature</td><td>{vitals.get('temperature')}°F</td><td>97–99°F</td></tr>
    </table>
    <br>
    <p style="color:gray;">This is an automated alert from the Patient Health Monitoring System.</p>
    </body></html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = SENDER_EMAIL
    msg["To"]      = caretaker_email
    msg.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, caretaker_email, msg.as_string())
        print(f"[EMAIL] Alert sent to {caretaker_email} for patient {patient_name}")
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")