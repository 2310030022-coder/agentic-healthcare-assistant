
import sqlite3
from pathlib import Path

DB_PATH = Path("data/healthcare.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            diagnosis TEXT NOT NULL,
            treatment TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_id) REFERENCES patients(id)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_time TEXT NOT NULL,
            status TEXT DEFAULT 'Booked',
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        );

        CREATE UNIQUE INDEX IF NOT EXISTS
        unique_doctor_slot
        ON appointments(doctor_id, appointment_time)
        WHERE status = 'Booked';
        """)

        conn.executemany(
            "INSERT OR IGNORE INTO patients VALUES (?, ?, ?)",
            [
                (1, "Rahul Sharma", 70),
                (2, "Priya Mehta", 35),
                (3, "Amit Kumar", 52)
            ]
        )

        conn.executemany(
            "INSERT OR IGNORE INTO doctors VALUES (?, ?, ?)",
            [
                (1, "Dr. Ananya Rao", "Nephrology"),
                (2, "Dr. Vikram Singh", "Cardiology"),
                (3, "Dr. Meera Patel", "General Medicine")
            ]
        )

        conn.commit()


if __name__ == "__main__":
    initialize_database()
    print("Healthcare database initialized successfully.")
  
