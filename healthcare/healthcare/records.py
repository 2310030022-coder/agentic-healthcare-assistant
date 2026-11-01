
from healthcare.database import get_connection


def get_patients():
    """Retrieve all registered patients."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM patients ORDER BY name"
        ).fetchall()

    return [dict(row) for row in rows]


def get_patient(patient_id):
    """Retrieve one patient by ID."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM patients WHERE id = ?",
            (patient_id,)
        ).fetchone()

    return dict(row) if row else None


def add_medical_record(patient_id, diagnosis, treatment, notes):
    """Add a new medical record for a patient."""
    if not diagnosis or not diagnosis.strip():
        return {
            "success": False,
            "message": "Diagnosis cannot be empty."
        }

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
            INSERT INTO medical_records
            (patient_id, diagnosis, treatment, notes)
            VALUES (?, ?, ?, ?)
            """,
            (patient_id, diagnosis.strip(), treatment, notes)
        )

        record_id = cursor.lastrowid
        conn.commit()

    return {
        "success": True,
        "record_id": record_id,
        "message": "Medical record added successfully."
    }


def get_medical_history(patient_id):
    """Retrieve the complete medical history of a patient."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, diagnosis, treatment, notes, created_at
            FROM medical_records
            WHERE patient_id = ?
            ORDER BY created_at DESC, id DESC
            """,
            (patient_id,)
        ).fetchall()

    return [dict(row) for row in rows]


def update_medical_record(record_id, diagnosis, treatment, notes):
    """Update an existing medical record."""
    if not diagnosis or not diagnosis.strip():
        return {
            "success": False,
            "message": "Diagnosis cannot be empty."
        }

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE medical_records
            SET diagnosis = ?, treatment = ?, notes = ?
            WHERE id = ?
            """,
            (diagnosis.strip(), treatment, notes, record_id)
        )

        conn.commit()

        if cursor.rowcount == 0:
            return {
                "success": False,
                "message": "Medical record not found."
            }

    return {
        "success": True,
        "message": "Medical record updated successfully."
    }


def generate_history_context(patient_id):
    """Prepare patient history for the AI summarization agent."""
    patient = get_patient(patient_id)

    if patient is None:
        return "Patient not found."

    history = get_medical_history(patient_id)

    if not history:
        return (
            f"Patient: {patient['name']}\n"
            f"Age: {patient['age']}\n"
            "No medical history is currently recorded."
        )

    lines = [
        f"Patient: {patient['name']}",
        f"Age: {patient['age']}",
        "",
        "Medical History:"
    ]

    for record in history:
        lines.extend([
            f"Date: {record['created_at']}",
            f"Diagnosis: {record['diagnosis']}",
            f"Treatment: {record['treatment'] or 'Not recorded'}",
            f"Notes: {record['notes'] or 'None'}",
            ""
        ])

    return "\n".join(lines)
