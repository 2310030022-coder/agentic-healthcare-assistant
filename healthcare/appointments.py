
import sqlite3
from datetime import datetime, timedelta

from healthcare.database import get_connection


def get_doctors(specialization=None):
    """Retrieve doctors, optionally by specialization."""
    with get_connection() as conn:
        if specialization:
            rows = conn.execute(
                """
                SELECT * FROM doctors
                WHERE LOWER(specialization) LIKE ?
                ORDER BY name
                """,
                (f"%{specialization.lower()}%",)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM doctors ORDER BY name"
            ).fetchall()

    return [dict(row) for row in rows]


def get_available_slots(doctor_id, days=7):
    """Find unbooked appointment slots for a doctor."""
    with get_connection() as conn:
        doctor = conn.execute(
            "SELECT id FROM doctors WHERE id = ?",
            (doctor_id,)
        ).fetchone()

        if doctor is None:
            return []

        booked = conn.execute(
            """
            SELECT appointment_time FROM appointments
            WHERE doctor_id = ? AND status = 'Booked'
            """,
            (doctor_id,)
        ).fetchall()

    booked_times = {row["appointment_time"] for row in booked}

    now = datetime.now()
    slots = []

    for offset in range(days):
        day = (now + timedelta(days=offset)).date()

        if day.weekday() >= 5:
            continue

        for hour in [9, 10, 11, 14, 15, 16]:
            slot = datetime.combine(
                day, datetime.min.time()
            ).replace(hour=hour)

            slot_string = slot.strftime("%Y-%m-%d %H:%M")

            if slot > now and slot_string not in booked_times:
                slots.append(slot_string)

    return slots


def book_appointment(patient_id, doctor_id, appointment_time):
    """Book an available slot without double-booking."""
    try:
        requested_time = datetime.strptime(
            appointment_time, "%Y-%m-%d %H:%M"
        )
    except (ValueError, TypeError):
        return {
            "success": False,
            "message": "Invalid appointment date or time."
        }

    if requested_time <= datetime.now():
        return {
            "success": False,
            "message": "Cannot book an appointment in the past."
        }

    if appointment_time not in get_available_slots(doctor_id):
        return {
            "success": False,
            "message": "This appointment slot is unavailable."
        }

    try:
        with get_connection() as conn:
            patient = conn.execute(
                "SELECT id FROM patients WHERE id = ?",
                (patient_id,)
            ).fetchone()

            if patient is None:
                return {
                    "success": False,
                    "message": "Patient not found."
                }

            cursor = conn.execute(
                """
                INSERT INTO appointments
                (patient_id, doctor_id, appointment_time, status)
                VALUES (?, ?, ?, 'Booked')
                """,
                (patient_id, doctor_id, appointment_time)
            )

            appointment_id = cursor.lastrowid
            conn.commit()

        return {
            "success": True,
            "appointment_id": appointment_id,
            "message": "Appointment booked successfully."
        }

    except sqlite3.IntegrityError:
        return {
            "success": False,
            "message": "Slot already booked or invalid patient/doctor."
        }


def get_patient_appointments(patient_id):
    """Retrieve a patient's appointments."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                a.id,
                a.appointment_time,
                a.status,
                d.name AS doctor_name,
                d.specialization
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.patient_id = ?
            ORDER BY a.appointment_time DESC
            """,
            (patient_id,)
        ).fetchall()

    return [dict(row) for row in rows]


def cancel_appointment(appointment_id):
    """Cancel an existing appointment."""
    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE appointments
            SET status = 'Cancelled'
            WHERE id = ? AND status = 'Booked'
            """,
            (appointment_id,)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": "Active appointment not found."
            }

    return {
        "success": True,
        "message": "Appointment cancelled successfully."
    }
