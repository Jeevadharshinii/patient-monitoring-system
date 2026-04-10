import sqlite3
import hashlib
from flask import g
import os

DATABASE = os.path.join(os.path.dirname(__file__), "db", "patient_app.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

def hash_password(pw): return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL CHECK(role IN ('doctor','caretaker')),
            email         TEXT,
            created_at    DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT NOT NULL,
            age            INTEGER,
            dob            TEXT,
            gender         TEXT,
            img            TEXT,
            heart_rate     TEXT,
            blood_pressure TEXT,
            oxygen_level   TEXT,
            temperature    TEXT,
            created_at     DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS medical_history (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER REFERENCES patients(id),
            note       TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS caretaker_patients (
            user_id    INTEGER REFERENCES users(id),
            patient_id INTEGER REFERENCES patients(id),
            PRIMARY KEY (user_id, patient_id)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vitals_history (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id    INTEGER REFERENCES patients(id),
            recorded_date TEXT NOT NULL,
            heart_rate    REAL,
            systolic_bp   REAL,
            diastolic_bp  REAL,
            oxygen_level  REAL,
            temperature   REAL
        )
    """)

    # Add email column if missing (for existing DBs)
    try:
        cur.execute("ALTER TABLE users ADD COLUMN email TEXT")
        conn.commit()
    except:
        pass

    conn.commit()

    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        _seed(conn, cur)
        conn.commit()
    else:
        # Update emails if not set
        cur.execute("UPDATE users SET email=? WHERE username=?", ("herejeevadharshini@gmail.com", "care1"))
        cur.execute("UPDATE users SET email=? WHERE username=?", ("herejeevadharshini@gmail.com", "care2"))
        conn.commit()

    conn.close()

def _seed(conn, cur):
    print("[DB] Seeding initial data...")
    cur.execute("INSERT INTO users (username, password_hash, role, email) VALUES (?,?,?,?)",
                ("doctor1", hash_password("doc123"), "doctor", "herejeevadharshini@gmail.com"))
    cur.execute("INSERT INTO users (username, password_hash, role, email) VALUES (?,?,?,?)",
                ("care1", hash_password("care123"), "caretaker", "herejeevadharshini@gmail.com"))
    cur.execute("INSERT INTO users (username, password_hash, role, email) VALUES (?,?,?,?)",
                ("care2", hash_password("care456"), "caretaker", "herejeevadharshini@gmail.com"))

    patients = [
        (1,"John Doe",65,"1959-01-12","Male","https://randomuser.me/api/portraits/men/11.jpg","78 bpm","120/80 mmHg","98%","98.6°F"),
        (2,"Ram",23,"2002-06-18","Male","https://randomuser.me/api/portraits/men/22.jpg","82 bpm","118/76 mmHg","97%","98.4°F"),
        (3,"Priya Sharma",27,"1998-01-20","Female","https://randomuser.me/api/portraits/women/30.jpg","75 bpm","115/78 mmHg","99%","98.2°F"),
    ]
    for p in patients:
        cur.execute("INSERT INTO patients (id,name,age,dob,gender,img,heart_rate,blood_pressure,oxygen_level,temperature) VALUES (?,?,?,?,?,?,?,?,?,?)", p)

    for pid, note in [(1,"Mild hypertension"),(1,"Recovered from COVID-19"),(2,"Seasonal allergies"),(2,"Minor surgery 2018"),(3,"Asthma"),(3,"Annual respiratory check-up")]:
        cur.execute("INSERT INTO medical_history (patient_id, note) VALUES (?,?)", (pid, note))

    cur.execute("INSERT INTO caretaker_patients VALUES (2,1)")
    cur.execute("INSERT INTO caretaker_patients VALUES (3,2)")

    import random, datetime
    base_date = datetime.date.today() - datetime.timedelta(days=6)
    vitals_seed = {
        1: dict(hr=78, sys=120, dia=80, oxy=98.0, temp=98.6),
        2: dict(hr=82, sys=118, dia=76, oxy=97.0, temp=98.4),
        3: dict(hr=75, sys=115, dia=78, oxy=99.0, temp=98.2),
    }
    for day_offset in range(7):
        date_str = (base_date + datetime.timedelta(days=day_offset)).isoformat()
        for pid, v in vitals_seed.items():
            cur.execute(
                "INSERT INTO vitals_history (patient_id,recorded_date,heart_rate,systolic_bp,diastolic_bp,oxygen_level,temperature) VALUES (?,?,?,?,?,?,?)",
                (pid, date_str, round(v["hr"]+random.uniform(-5,5),1), round(v["sys"]+random.uniform(-5,5),1),
                 round(v["dia"]+random.uniform(-3,3),1), round(v["oxy"]+random.uniform(-1,1),1), round(v["temp"]+random.uniform(-0.3,0.3),1))
            )
    print("[DB] Seed complete.")