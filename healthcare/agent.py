
from healthcare.config import generate_ai_response
from healthcare.records import generate_history_context
from healthcare.appointments import (
    get_doctors,
    get_available_slots,
)


DEPARTMENT_KEYWORDS = {
    "Nephrology": [
        "kidney", "renal", "urinary", "bladder",
    ],
    "Cardiology": [
        "heart", "cardiac", "palpitation",
    ],
    "Neurology": [
        "brain", "headache", "migraine", "nerve",
    ],
    "Orthopedics": [
        "bone", "joint", "fracture", "knee",
    ],
    "Dermatology": [
        "skin", "hair", "rash", "acne",
    ],
    "Gastroenterology": [
        "stomach", "digestive", "gastric",
    ],
    "Endocrinology": [
        "diabetes", "thyroid", "hormone",
    ],
    "Pulmonology": [
        "lung", "breathing", "asthma",
    ],
    "Ophthalmology": [
        "eye", "vision",
    ],
    "ENT": [
        "ear", "nose", "throat",
    ],
    "Gynecology": [
        "menstrual", "pregnancy", "gynecology",
    ],
    "Psychiatry": [
        "anxiety", "depression", "psychiatry",
    ],
    "Pediatrics": [
        "child", "pediatric",
    ],
}


def detect_department(query):
    query = query.lower()

    for department, keywords in DEPARTMENT_KEYWORDS.items():
        if any(word in query for word in keywords):
            return department

    return "General Medicine"


def run_healthcare_agent(user_query, patient_id=None):

    if not str(user_query).strip():
        return {
            "response": "Please enter a healthcare request.",
            "plan": [],
            "execution_trace": [],
            "medical_sources": [],
            "doctors": [],
        }

    plan = [
        "Understand patient request",
        "Retrieve relevant patient history",
        "Find appropriate department",
        "Check doctor appointment availability",
        "Generate response using Gemini AI",
    ]

    trace = []
    department = detect_department(user_query)

    # -----------------------------------------
    # PATIENT HISTORY
    # -----------------------------------------

    history = "No patient history provided."

    if patient_id is not None:
        try:
            history = generate_history_context(patient_id)
            trace.append(
                "Patient medical history retrieved"
            )
        except Exception as exc:
            trace.append(
                "Patient history unavailable: "
                + str(exc)[:150]
            )

    # -----------------------------------------
    # DOCTOR AVAILABILITY
    # -----------------------------------------

    doctor_details = []

    try:
        doctors = [
            dict(doctor)
            for doctor in get_doctors()
        ]

        matched_doctors = [
            doctor
            for doctor in doctors
            if doctor["specialization"] == department
        ]

        for doctor in matched_doctors[:5]:
            try:
                slots = get_available_slots(
                    doctor["id"],
                    days=7,
                )

                doctor_details.append({
                    "doctor": doctor["name"],
                    "department": department,
                    "available_slots": list(slots)[:5],
                })

            except Exception as exc:
                trace.append(
                    f"Availability check failed for "
                    f"{doctor['name']}: {str(exc)[:100]}"
                )

        trace.append(
            f"Checked {len(matched_doctors)} "
            f"doctors in {department}"
        )

    except Exception as exc:
        trace.append(
            "Doctor directory unavailable: "
            + str(exc)[:150]
        )

    # -----------------------------------------
    # GEMINI PROMPT
    # -----------------------------------------

    prompt = f"""
You are MediFlow AI, a helpful healthcare information
and appointment management assistant.

USER REQUEST:
{user_query}

SUGGESTED DEPARTMENT:
{department}

PATIENT MEDICAL HISTORY:
{history}

DOCTOR APPOINTMENT INFORMATION:
{doctor_details}

INSTRUCTIONS:
1. Answer the user's question clearly.
2. Summarize documented medical history if requested.
3. Explain medical topics in understandable language.
4. Mention relevant available doctors when useful.
5. Never invent patient records or appointment slots.
6. Never claim an appointment was booked.
7. Do not provide a definitive diagnosis.
8. Do not prescribe medication.
9. Recommend professional evaluation when appropriate.
10. For emergencies, recommend urgent medical attention.

Keep the answer helpful and organized.
"""

    # -----------------------------------------
    # GEMINI RESPONSE
    # -----------------------------------------

    try:
        response = generate_ai_response(prompt)

        trace.append(
            "Gemini AI generated response successfully"
        )

    except Exception as exc:
        # Return a readable message rather than
        # crashing the entire Streamlit application.
        error_message = str(exc)

        trace.append(
            "Gemini generation unavailable: "
            + error_message[:200]
        )

        response = (
            "Gemini AI is currently unavailable.\n\n"
            + error_message
            + "\n\nYou can still use patient records, "
            "doctor selection, and appointment booking."
        )

    return {
        "response": response,
        "plan": plan,
        "execution_trace": trace,
        "medical_sources": [],
        "department": department,
        "doctors": doctor_details,
    }
