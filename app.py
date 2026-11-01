
import streamlit as st
import pandas as pd
from datetime import date
from urllib.parse import quote_plus

from healthcare.database import initialize_database, get_connection
from healthcare.records import (
    get_patients, get_patient, get_medical_history,
    add_medical_record, update_medical_record,
    generate_history_context
)
from healthcare.appointments import (
    get_doctors, get_available_slots, book_appointment,
    get_patient_appointments, cancel_appointment
)

# =====================================================
# APP CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="MediFlow AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

initialize_database()

# =====================================================
# DATABASE: CONSULTATIONS AND PATIENT RECOVERY
# =====================================================

def initialize_health_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consultations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                appointment_id INTEGER NOT NULL UNIQUE,
                doctor_name TEXT NOT NULL,
                consultation_date TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                prescription TEXT NOT NULL,
                instructions TEXT,
                followup_date TEXT,
                baseline_pain INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS recovery_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                consultation_id INTEGER NOT NULL,
                entry_date TEXT NOT NULL,
                pain_score INTEGER NOT NULL,
                symptoms TEXT NOT NULL,
                adherence TEXT NOT NULL,
                heart_rate INTEGER,
                systolic INTEGER,
                diastolic INTEGER,
                oxygen REAL,
                temperature REAL,
                patient_notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()


initialize_health_tables()


def fetch_rows(query, params=()):
    with get_connection() as conn:
        return [
            dict(row)
            for row in conn.execute(query, params).fetchall()
        ]


def rows(data):
    return [dict(x) for x in (data or [])]


def show_table(data):
    data = rows(data)
    if data:
        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No records available yet.")


def navigate(page):
    st.session_state["next_page"] = page
    st.rerun()


def notify(message):
    st.session_state["notice"] = message
    st.rerun()


def operation_success(result):
    if isinstance(result, dict):
        return result.get("success", True)
    return result is not False


def google_search(query):
    return "https://www.google.com/search?q=" + quote_plus(query)


# =====================================================
# PROFESSIONAL UI DESIGN
# =====================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg,#eff7ff,#f7f1ff);
    font-family: "Segoe UI", Arial, sans-serif;
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.stApp h1 {
    font-size: 2.3rem !important;
    font-weight: 850 !important;
    color: #102b55;
}

.stApp h2 {
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    color: #153760;
}

.stApp h3 {
    font-size: 1.4rem !important;
    font-weight: 800 !important;
    color: #173c69;
}

.stApp p {
    font-size: 1.08rem;
    line-height: 1.6;
}

.stApp [data-testid="stWidgetLabel"] p {
    font-size: 1.13rem !important;
    font-weight: 750 !important;
    color: #123967 !important;
}

.stApp input,
.stApp textarea,
.stApp [data-baseweb="select"] {
    font-size: 1.08rem !important;
}

.stButton > button {
    border-radius: 12px;
    min-height: 48px;
    font-size: 1.04rem !important;
    font-weight: 800 !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#1766e9,#7747e7);
    color: white;
    border: none;
}

[data-testid="stForm"] {
    background: linear-gradient(140deg,#ffffff,#f0f7ff);
    padding: 24px !important;
    border: 2px solid #b9d5fa;
    border-radius: 17px;
}

[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #dce6f5;
}

/* SIDEBAR */

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#173372,#176b9b);
    min-width: 300px !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: white !important;
}

section[data-testid="stSidebar"] h3 {
    background: rgba(255,255,255,.14);
    border-left: 4px solid #70d9ff;
    padding: 12px;
    border-radius: 10px;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] [role="radiogroup"] p {
    font-size: 1.07rem !important;
    font-weight: 750 !important;
    color: white !important;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] [role="radiogroup"] label {
    padding: 9px !important;
    border-radius: 10px;
}

section[data-testid="stSidebar"]
[data-testid="stRadio"] [role="radiogroup"]
label:has(input:checked) {
    background: rgba(95,204,255,.27);
    box-shadow: inset 4px 0 #67e8f9;
}

section[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #132a4b !important;
    -webkit-text-fill-color: #132a4b !important;
}

section[data-testid="stSidebar"] .stButton button {
    background: white !important;
    color: #173372 !important;
}

/* HEADER */

.hero {
    background: linear-gradient(100deg,#1765dc,#6745d6);
    padding: 30px;
    border-radius: 20px;
    margin-bottom: 24px;
}

.hero h1,
.hero p {
    color: white !important;
}

/* DASHBOARD CARDS */

.dashboard-card {
    min-height: 195px;
    padding: 22px 18px;
    border-radius: 18px;
    box-shadow: 0 8px 24px rgba(25,60,130,.12);
    margin-bottom: 12px;
}

.dashboard-card h3 {
    color: #172554 !important;
    font-size: 1.4rem !important;
}

.dashboard-card p {
    color: #334155 !important;
}

.card-patients {
    background: linear-gradient(135deg,#dbeafe,#bfdbfe);
    border-left: 6px solid #2563eb;
}

.card-appointments {
    background: linear-gradient(135deg,#dcfce7,#bbf7d0);
    border-left: 6px solid #16a34a;
}

.card-records {
    background: linear-gradient(135deg,#f3e8ff,#e9d5ff);
    border-left: 6px solid #9333ea;
}

.card-search {
    background: linear-gradient(135deg,#ffedd5,#fed7aa);
    border-left: 6px solid #ea580c;
}

/* HIGHLIGHTED SECTIONS */

.section-banner {
    padding: 18px 23px;
    border-radius: 15px;
    background: linear-gradient(100deg,#dcecff,#e8e3ff);
    border-left: 7px solid #2563eb;
    margin: 12px 0 22px;
}

.section-banner h3 {
    color: #14376c !important;
    margin: 0 0 8px !important;
}

.section-banner p {
    color: #304a6a !important;
    margin: 0 !important;
}

.section-banner.green {
    background: linear-gradient(100deg,#e0f9e9,#e7f6ff);
    border-left-color: #16a34a;
}

.section-banner.purple {
    background: linear-gradient(100deg,#f0e5ff,#e9f0ff);
    border-left-color: #9333ea;
}

[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


def banner(title, description, color=""):
    st.markdown(
        f'<div class="section-banner {color}">'
        f"<h3>{title}</h3>"
        f"<p>{description}</p>"
        "</div>",
        unsafe_allow_html=True
    )


# =====================================================
# DOCTOR PHOTOS
# Unique illustrative portraits for sample doctors
# =====================================================

DOCTOR_IMAGES = {
    "Dr. Kavya Reddy":
        "https://randomuser.me/api/portraits/women/44.jpg",
    "Dr. Arjun Nair":
        "https://randomuser.me/api/portraits/men/32.jpg",
    "Dr. Sneha Kapoor":
        "https://randomuser.me/api/portraits/women/68.jpg",
    "Dr. Rohan Desai":
        "https://randomuser.me/api/portraits/men/46.jpg",
    "Dr. Ishita Verma":
        "https://randomuser.me/api/portraits/women/33.jpg",
    "Dr. Aditya Menon":
        "https://randomuser.me/api/portraits/men/75.jpg",
    "Dr. Neha Shah":
        "https://randomuser.me/api/portraits/women/65.jpg",
    "Dr. Vivek Bansal":
        "https://randomuser.me/api/portraits/men/52.jpg",
    "Dr. Pooja Sinha":
        "https://randomuser.me/api/portraits/women/79.jpg",
    "Dr. Nikhil Joshi":
        "https://randomuser.me/api/portraits/men/22.jpg",
    "Dr. Ritu Malhotra":
        "https://randomuser.me/api/portraits/women/21.jpg",
    "Dr. Aarav Khanna":
        "https://randomuser.me/api/portraits/men/62.jpg",
    "Dr. Diya Sharma":
        "https://randomuser.me/api/portraits/women/57.jpg",
    "Dr. Simran Gupta":
        "https://randomuser.me/api/portraits/women/26.jpg",
}

DEFAULT_IMAGE = (
    "https://api.dicebear.com/9.x/initials/png?seed=Doctor"
)

DOCTOR_DATA = [
    ("Dr. Kavya Reddy", "Neurology"),
    ("Dr. Arjun Nair", "Orthopedics"),
    ("Dr. Sneha Kapoor", "Dermatology"),
    ("Dr. Rohan Desai", "Gastroenterology"),
    ("Dr. Ishita Verma", "Endocrinology"),
    ("Dr. Aditya Menon", "Pulmonology"),
    ("Dr. Neha Shah", "ENT"),
    ("Dr. Vivek Bansal", "Ophthalmology"),
    ("Dr. Pooja Sinha", "Gynecology"),
    ("Dr. Nikhil Joshi", "Psychiatry"),
    ("Dr. Ritu Malhotra", "Pediatrics"),
    ("Dr. Aarav Khanna", "Nephrology"),
    ("Dr. Diya Sharma", "Cardiology"),
    ("Dr. Simran Gupta", "General Medicine"),
]

with get_connection() as conn:
    existing = {
        (r["name"], r["specialization"])
        for r in conn.execute(
            "SELECT name, specialization FROM doctors"
        )
    }

    for name, specialization in DOCTOR_DATA:
        if (name, specialization) not in existing:
            conn.execute(
                "INSERT INTO doctors(name,specialization) VALUES (?,?)",
                (name, specialization)
            )

    conn.commit()


# =====================================================
# DEPARTMENT DETECTION
# =====================================================

DEPARTMENT_KEYWORDS = {
    "Nephrology": ["kidney", "renal", "urinary", "bladder"],
    "Cardiology": ["heart", "cardiac", "palpitation"],
    "Neurology": ["brain", "headache", "migraine"],
    "Orthopedics": ["bone", "joint", "fracture", "knee"],
    "Dermatology": ["skin", "hair", "rash"],
    "Gastroenterology": ["stomach", "digestive"],
    "Endocrinology": ["diabetes", "thyroid"],
    "Pulmonology": ["lung", "breathing", "asthma"],
    "ENT": ["ear", "nose", "throat"],
    "Ophthalmology": ["eye", "vision"],
    "Gynecology": ["menstrual", "pregnancy"],
    "Psychiatry": ["anxiety", "depression"],
    "Pediatrics": ["child", "pediatric"],
}


def department_for(query):
    query = query.lower()

    for department, words in DEPARTMENT_KEYWORDS.items():
        if any(word in query for word in words):
            return department

    return "General Medicine"


# =====================================================
# SIDEBAR
# =====================================================

PAGES = [
    "🏠 Dashboard",
    "👤 Patients",
    "📅 Appointments",
    "📋 Medical Records",
    "💊 Doctor Consultation",
    "🩺 History Summary",
    "🔎 Medical Research",
    "🔍 Google Health Assistant",
    "🧠 FAISS Memory",
    "❤️ Health Monitoring",
]

if "next_page" in st.session_state:
    st.session_state["page"] = (
        st.session_state.pop("next_page")
    )

with st.sidebar:
    st.title("🏥 MediFlow AI")

    st.markdown(
        "**HEALTHCARE WORKSPACE**"
    )

    page = st.radio(
        "Modules",
        PAGES,
        key="page"
    )

    st.divider()
    st.subheader("Patient Workspace")

    patients = rows(get_patients())

    patient_options = {
        f"{p['name']} · ID {p['id']}": p["id"]
        for p in patients
    }

    if patient_options:
        selected = st.selectbox(
            "Select Patient",
            list(patient_options),
            key="patient_choice"
        )

        patient_id = patient_options[selected]
        patient_row = get_patient(patient_id)

        patient = (
            dict(patient_row)
            if patient_row
            else None
        )

        if patient:
            st.write(
                f"**{patient['name']}** · "
                f"{patient['age']} years"
            )
    else:
        patient_id = None
        patient = None
        st.info("Register a patient first.")

    if st.button(
        "➕ Register New Patient",
        use_container_width=True
    ):
        navigate("👤 Patients")


# =====================================================
# SUCCESS NOTIFICATIONS
# =====================================================

if "notice" in st.session_state:
    message = st.session_state.pop("notice")

    st.success(message, icon="✅")
    st.toast(message, icon="🎉")


# =====================================================
# MAIN HEADER
# =====================================================

st.markdown("""
<div class="hero">
    <h1>🏥 MediFlow AI</h1>
    <p>
        Patient Management · Appointments ·
        Doctor Consultation · Recovery Monitoring
    </p>
</div>
""", unsafe_allow_html=True)


# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    doctors = rows(get_doctors())

    appointments = (
        rows(get_patient_appointments(patient_id))
        if patient_id
        else []
    )

    a, b, c, d = st.columns(4)

    a.metric("Patients", len(patients))
    b.metric("Doctors", len(doctors))

    c.metric(
        "Departments",
        len({d["specialization"] for d in doctors})
    )

    d.metric("Patient Appointments", len(appointments))

    st.subheader("Explore the Platform")

    modules = [
        (
            "👤 Patients",
            "Register patients and manage profiles.",
            "card-patients",
            "👤 Patients"
        ),
        (
            "📅 Appointments",
            "Choose doctors and book consultations.",
            "card-appointments",
            "📅 Appointments"
        ),
        (
            "📋 Medical Records",
            "Manage diagnoses and treatments.",
            "card-records",
            "📋 Medical Records"
        ),
        (
            "❤️ Recovery",
            "Track treatment and patient improvement.",
            "card-search",
            "❤️ Health Monitoring"
        ),
    ]

    cols = st.columns(4)

    for i, (title, description, css, destination) in enumerate(modules):
        with cols[i]:
            st.markdown(
                f"""
                <div class="dashboard-card {css}">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                f"Open {title}",
                key=f"dashboard_{i}",
                type="primary",
                use_container_width=True
            ):
                navigate(destination)

    st.subheader("Recent Appointments")
    show_table(appointments[:5])


# =====================================================
# PATIENT REGISTRATION
# =====================================================

elif page == "👤 Patients":

    st.header("👤 Patient Registration")

    banner(
        "➕ Add a New Patient",
        "Enter the patient's name and age to create "
        "a new patient profile."
    )

    with st.form("register_patient", clear_on_submit=True):

        name = st.text_input(
            "👤 Full Patient Name",
            placeholder="Enter patient's full name"
        )

        age = st.number_input(
            "🎂 Patient Age",
            min_value=0,
            max_value=120,
            value=30
        )

        submitted = st.form_submit_button(
            "✅ Register Patient",
            type="primary",
            use_container_width=True
        )

    if submitted:
        if len(name.strip()) < 2:
            st.error("Enter a valid patient name.")
        else:
            try:
                with get_connection() as conn:
                    cursor = conn.execute(
                        "INSERT INTO patients(name,age) VALUES (?,?)",
                        (name.strip(), int(age))
                    )

                    conn.commit()

                notify(
                    f"Patient {name.strip()} registered successfully! "
                    f"ID: {cursor.lastrowid}"
                )

            except Exception as exc:
                st.error(f"Registration failed: {exc}")

    banner(
        "📋 Registered Patients",
        "View the patients registered in the system.",
        "green"
    )

    show_table(get_patients())


# =====================================================
# APPOINTMENTS
# =====================================================

elif page == "📅 Appointments":

    st.header("📅 Smart Appointment Booking")

    banner(
        "🩺 Select Department and Doctor",
        "Choose the consultation type, doctor, "
        "and appointment slot.",
        "green"
    )

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    st.info(f"Patient: **{patient['name']}**")

    guide = {
        "Kidney or urinary concerns": "Nephrology",
        "Heart concerns": "Cardiology",
        "Headache or nerve concerns": "Neurology",
        "Bones and joints": "Orthopedics",
        "Skin and hair": "Dermatology",
        "Digestive concerns": "Gastroenterology",
        "Diabetes or thyroid": "Endocrinology",
        "Breathing concerns": "Pulmonology",
        "Ear, nose or throat": "ENT",
        "Eye concerns": "Ophthalmology",
        "Women's health": "Gynecology",
        "Mental health": "Psychiatry",
        "Children's health": "Pediatrics",
        "General consultation": "General Medicine"
    }

    concern = st.selectbox(
        "Step 1 — Consultation Type",
        list(guide)
    )

    doctors = rows(get_doctors())

    departments = sorted({
        d["specialization"]
        for d in doctors
    })

    if not departments:
        st.warning("No doctors available.")
        st.stop()

    department = st.selectbox(
        "Step 2 — Department",
        departments,
        index=(
            departments.index(guide[concern])
            if guide[concern] in departments
            else 0
        ),
        key=f"dept_{concern}"
    )

    filtered = [
        d for d in doctors
        if d["specialization"] == department
    ]

    if not filtered:
        st.warning("No matching doctors.")
        st.stop()

    doctor_options = {
        f"{d['name']} · {department}": d["id"]
        for d in filtered
    }

    selected = st.selectbox(
        "Step 3 — Choose Doctor",
        list(doctor_options)
    )

    doctor_id = doctor_options[selected]

    doctor = next(
        d for d in filtered
        if d["id"] == doctor_id
    )

    with st.container(border=True):
        photo, details = st.columns([1, 3])

        with photo:
            st.image(
                DOCTOR_IMAGES.get(
                    doctor["name"],
                    DEFAULT_IMAGE
                ),
                width=170
            )

        with details:
            st.subheader(doctor["name"])
            st.write(f"**Department:** {department}")
            st.write(f"**Patient:** {patient['name']}")
            st.caption("Illustrative doctor portrait")

    try:
        slots = list(
            get_available_slots(doctor_id, days=7)
        )
    except Exception as exc:
        slots = []
        st.error(f"Could not load slots: {exc}")

    if slots:
        slot = st.selectbox(
            "Step 4 — Appointment Slot",
            slots
        )

        confirmed = st.checkbox(
            "I confirm this appointment"
        )

        if st.button(
            "✅ Confirm Booking",
            type="primary",
            disabled=not confirmed,
            use_container_width=True
        ):
            try:
                result = book_appointment(
                    patient_id,
                    doctor_id,
                    slot
                )

                if operation_success(result):
                    notify(
                        f"Appointment booked successfully "
                        f"with {doctor['name']} on {slot}!"
                    )
                else:
                    st.error("Booking was unsuccessful.")

            except Exception as exc:
                st.error(f"Booking failed: {exc}")
    else:
        st.warning("No available slots for this doctor.")

    if st.button("💊 Record Consultation After Visit"):
        navigate("💊 Doctor Consultation")

    st.subheader("Appointment History")

    appointments = rows(
        get_patient_appointments(patient_id)
    )

    show_table(appointments)

    active = [
        a for a in appointments
        if str(a.get("status", "")).lower() == "booked"
    ]

    if active:
        choices = {
            f"#{a['id']} · {a['appointment_time']}": a["id"]
            for a in active
        }

        selected_cancel = st.selectbox(
            "Select Appointment to Cancel",
            list(choices)
        )

        if st.button("Cancel Selected Appointment"):
            try:
                result = cancel_appointment(
                    choices[selected_cancel]
                )

                if operation_success(result):
                    notify("Appointment cancelled successfully.")
                else:
                    st.error("Cancellation was unsuccessful.")

            except Exception as exc:
                st.error(f"Cancellation failed: {exc}")


# =====================================================
# MEDICAL RECORDS
# =====================================================

elif page == "📋 Medical Records":

    st.header("📋 Medical Records")

    banner(
        "📝 Patient Medical Records",
        "Review, add, and update patient medical records.",
        "purple"
    )

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    records = rows(
        get_medical_history(patient_id)
    )

    show_table(records)

    banner(
        "➕ Add Medical Record",
        "Enter the diagnosis, treatment, and notes."
    )

    with st.form("medical_record"):

        diagnosis = st.text_input(
            "Diagnosis or Condition"
        )

        treatment = st.text_area(
            "Treatment"
        )

        notes = st.text_area(
            "Medical Notes"
        )

        save = st.form_submit_button(
            "💾 Save Record",
            type="primary"
        )

    if save:
        if not diagnosis.strip():
            st.error("Enter a diagnosis.")
        else:
            try:
                add_medical_record(
                    patient_id,
                    diagnosis.strip(),
                    treatment,
                    notes
                )

                notify("Medical record saved successfully.")

            except Exception as exc:
                st.error(f"Save failed: {exc}")

    if records:
        st.subheader("Update Existing Record")

        choices = {
            f"#{r['id']} · {r['diagnosis']}": r
            for r in records
        }

        record = choices[
            st.selectbox("Select Record", list(choices))
        ]

        with st.form("update_record"):

            new_diagnosis = st.text_input(
                "Update Diagnosis",
                value=record.get("diagnosis") or ""
            )

            new_treatment = st.text_area(
                "Update Treatment",
                value=record.get("treatment") or ""
            )

            new_notes = st.text_area(
                "Update Notes",
                value=record.get("notes") or ""
            )

            update = st.form_submit_button(
                "Save Changes"
            )

        if update:
            try:
                update_medical_record(
                    record["id"],
                    new_diagnosis,
                    new_treatment,
                    new_notes
                )

                notify("Record updated successfully.")

            except Exception as exc:
                st.error(f"Update failed: {exc}")


# =====================================================
# DOCTOR CONSULTATION AND PRESCRIPTION
# =====================================================

elif page == "💊 Doctor Consultation":

    st.header("💊 Doctor Consultation & Prescription")

    banner(
        "🩺 Record Consultation After Appointment",
        "After the patient meets the doctor, record "
        "the diagnosis, actual prescription, and "
        "follow-up instructions.",
        "purple"
    )

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    st.info(f"Patient: **{patient['name']}**")

    st.warning(
        "This is a prototype record-entry form, not "
        "a verified doctor login. Only enter prescription "
        "information actually issued by the treating doctor."
    )

    appointments = rows(
        get_patient_appointments(patient_id)
    )

    existing_consultations = fetch_rows(
        """
        SELECT * FROM consultations
        WHERE patient_id=?
        ORDER BY consultation_date DESC, id DESC
        """,
        (patient_id,)
    )

    used_appointments = {
        c["appointment_id"]
        for c in existing_consultations
    }

    eligible = [
        a for a in appointments
        if a["id"] not in used_appointments
        and str(a.get("status", "")).lower()
        not in ("cancelled", "canceled")
    ]

    if eligible:

        options = {
            f"Appointment #{a['id']} · "
            f"{a.get('appointment_time', '')}": a
            for a in eligible
        }

        selected = st.selectbox(
            "Step 1 — Select Completed Appointment",
            list(options)
        )

        appointment = options[selected]

        doctors_by_id = {
            d["id"]: d["name"]
            for d in rows(get_doctors())
        }

        doctor_name = doctors_by_id.get(
            appointment.get("doctor_id"),
            "Assigned Doctor"
        )

        st.write(f"**Doctor:** {doctor_name}")

        with st.form("consultation_form"):

            consultation_date = st.date_input(
                "Step 2 — Consultation Date",
                value=date.today(),
                max_value=date.today()
            )

            visit_confirmed = st.checkbox(
                "I confirm the consultation took place "
                "and these details came from the doctor."
            )

            diagnosis = st.text_area(
                "Step 3 — Doctor's Diagnosis",
                placeholder="Enter documented diagnosis"
            )

            prescription = st.text_area(
                "Step 4 — Doctor-Issued Prescription",
                placeholder=(
                    "Enter prescribed medicine, dosage, "
                    "frequency and duration, or "
                    "'No medication prescribed'"
                )
            )

            instructions = st.text_area(
                "Doctor's Care Instructions"
            )

            followup = st.date_input(
                "Follow-up Date",
                value=date.today()
            )

            baseline_pain = st.slider(
                "Pain at Consultation (0–10)",
                0, 10, 5
            )

            save = st.form_submit_button(
                "💾 Save Consultation & Prescription",
                type="primary",
                use_container_width=True
            )

        if save:
            if not visit_confirmed:
                st.error(
                    "Confirm the consultation took place."
                )

            elif not diagnosis.strip() or not prescription.strip():
                st.error(
                    "Enter the diagnosis and actual "
                    "prescription details."
                )

            else:
                try:
                    with get_connection() as conn:
                        conn.execute(
                            """
                            INSERT INTO consultations (
                                patient_id,
                                appointment_id,
                                doctor_name,
                                consultation_date,
                                diagnosis,
                                prescription,
                                instructions,
                                followup_date,
                                baseline_pain
                            )
                            VALUES (?,?,?,?,?,?,?,?,?)
                            """,
                            (
                                patient_id,
                                appointment["id"],
                                doctor_name,
                                str(consultation_date),
                                diagnosis.strip(),
                                prescription.strip(),
                                instructions.strip(),
                                str(followup),
                                baseline_pain
                            )
                        )

                        conn.commit()

                    notify(
                        "Consultation and prescription saved! "
                        "Patient health monitoring is now available."
                    )

                except Exception as exc:
                    st.error(f"Save failed: {exc}")

    else:
        st.info(
            "No appointment is awaiting consultation. "
            "Book an appointment first."
        )

    st.subheader("Consultation History")

    for consultation in existing_consultations:
        with st.expander(
            f"{consultation['consultation_date']} · "
            f"{consultation['doctor_name']}"
        ):
            st.write(
                "**Diagnosis:**",
                consultation["diagnosis"]
            )

            st.write(
                "**Prescription:**",
                consultation["prescription"]
            )

            st.write(
                "**Instructions:**",
                consultation.get("instructions") or "None"
            )

            st.write(
                "**Follow-up Date:**",
                consultation.get("followup_date")
            )


# =====================================================
# HISTORY SUMMARY
# =====================================================

elif page == "🩺 History Summary":

    st.header("🩺 Patient History Summary")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    show_table(
        get_medical_history(patient_id)
    )

    if st.button(
        "📋 Generate History Summary",
        type="primary"
    ):
        try:
            context = generate_history_context(
                patient_id
            )

            st.session_state["history_summary"] = {
                "patient_id": patient_id,
                "text": str(context)
            }

            st.toast("History summary prepared!", icon="✅")

        except Exception as exc:
            st.error(f"History retrieval failed: {exc}")

    summary = st.session_state.get("history_summary")

    if summary and summary["patient_id"] == patient_id:
        st.subheader("Patient History")
        st.write(summary["text"])

    st.subheader("Consultations and Prescriptions")

    consultations = fetch_rows(
        """
        SELECT consultation_date, doctor_name,
               diagnosis, prescription,
               instructions, followup_date
        FROM consultations
        WHERE patient_id=?
        ORDER BY consultation_date DESC
        """,
        (patient_id,)
    )

    show_table(consultations)


# =====================================================
# GOOGLE MEDICAL RESEARCH
# =====================================================

elif page == "🔎 Medical Research":

    st.header("🔎 Medical Research via Google")

    banner(
        "🔍 Search Medical Topics",
        "Search Google and established healthcare websites."
    )

    topic = st.text_input(
        "Medical Topic",
        placeholder="e.g. chronic kidney disease"
    )

    if topic.strip():

        st.link_button(
            "🔍 Search Google",
            google_search(topic + " health information"),
            use_container_width=True
        )

        for title, domain in [
            ("MedlinePlus", "medlineplus.gov"),
            ("WHO", "who.int"),
            ("NHS", "nhs.uk"),
            ("CDC", "cdc.gov")
        ]:
            st.link_button(
                f"Search {title}",
                google_search(f"site:{domain} {topic}")
            )

    else:
        st.info("Enter a medical topic to begin.")


# =====================================================
# GOOGLE HEALTH ASSISTANT
# =====================================================

elif page == "🔍 Google Health Assistant":

    st.header("🔍 Google-Powered Healthcare Assistant")

    banner(
        "🩺 Healthcare Search and Patient Support",
        "View patient history, matching doctors, "
        "appointment information, and Google research.",
        "purple"
    )

    query = st.text_area(
        "Describe Your Request",
        placeholder="e.g. Find a cardiologist",
        height=140
    )

    if st.button(
        "🔍 Process Healthcare Request",
        type="primary",
        use_container_width=True
    ):

        if not query.strip():
            st.warning("Enter a request first.")

        else:
            department = department_for(query)

            history = "No patient history available."

            if patient_id:
                try:
                    history = str(
                        generate_history_context(patient_id)
                    )
                except Exception:
                    pass

            matching_doctors = [
                d for d in rows(get_doctors())
                if d["specialization"] == department
            ]

            details = []

            for doctor in matching_doctors[:5]:
                try:
                    slots = list(
                        get_available_slots(
                            doctor["id"],
                            days=7
                        )
                    )[:3]
                except Exception:
                    slots = []

                details.append({
                    "name": doctor["name"],
                    "slots": slots
                })

            st.session_state["search_result"] = {
                "patient_id": patient_id,
                "query": query,
                "department": department,
                "history": history,
                "doctors": details
            }

            st.toast("Request processed!", icon="✅")

    result = st.session_state.get("search_result")

    if result and result["patient_id"] == patient_id:

        st.success("Healthcare information retrieved.")

        st.subheader("Suggested Department")
        st.write(result["department"])

        st.caption(
            "Keyword-based routing, not a medical diagnosis."
        )

        st.subheader("Patient History")
        st.write(result["history"])

        st.subheader("Matching Doctors")

        for doctor in result["doctors"]:
            with st.container(border=True):
                st.write(f"**{doctor['name']}**")
                st.write(
                    "Available slots:",
                    doctor["slots"]
                )

        st.subheader("Google Health Research")

        # Do not send patient history to Google.
        search_topic = (
            result["department"] + " health information"
        )

        st.link_button(
            "🔍 Search Google",
            google_search(search_topic),
            use_container_width=True
        )

        st.link_button(
            "Search MedlinePlus",
            google_search(
                "site:medlineplus.gov " + search_topic
            )
        )

        if st.button("📅 Book Appointment"):
            navigate("📅 Appointments")


# =====================================================
# FAISS MEMORY
# =====================================================

elif page == "🧠 FAISS Memory":

    st.header("🧠 Patient Semantic Memory")

    banner(
        "🧠 Search Patient Memory",
        "Search saved patient information by meaning."
    )

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    query = st.text_input(
        "Search Patient Records"
    )

    if st.button(
        "🔍 Search Memory",
        type="primary"
    ):

        if not query.strip():
            st.warning("Enter a query.")

        else:
            try:
                from healthcare.memory import (
                    retrieve_patient_memory
                )

                matches = retrieve_patient_memory(
                    patient_id,
                    query
                )

                if not matches:
                    st.info("No matching memory found.")

                for i, item in enumerate(matches, 1):
                    with st.container(border=True):
                        st.subheader(f"Match {i}")
                        st.write(item.get("content", ""))

                        st.caption(
                            f"Similarity: "
                            f"{float(item.get('similarity', 0)):.3f}"
                        )

            except Exception as exc:
                st.error(f"Memory search failed: {exc}")


# =====================================================
# PATIENT HEALTH MONITORING
# =====================================================

elif page == "❤️ Health Monitoring":

    st.header("❤️ Patient Recovery & Health Monitoring")

    banner(
        "📈 Patient Treatment and Recovery",
        "Track the patient's health after their doctor "
        "consultation and prescription. Compare symptoms "
        "and recorded measurements over time.",
        "green"
    )

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    st.info(
        f"👤 Patient: **{patient['name']}** · "
        f"Age: {patient['age']} · ID: {patient_id}"
    )

    consultations = fetch_rows(
        """
        SELECT * FROM consultations
        WHERE patient_id=?
        ORDER BY consultation_date DESC, id DESC
        """,
        (patient_id,)
    )

    if not consultations:
        st.warning(
            "No doctor consultation recorded yet. "
            "First book an appointment, meet the doctor, "
            "and record the actual prescription."
        )

        if st.button("📅 Book Appointment"):
            navigate("📅 Appointments")

        if st.button("💊 Enter Doctor Consultation"):
            navigate("💊 Doctor Consultation")

        st.stop()

    options = {
        f"{c['consultation_date']} · "
        f"{c['doctor_name']} · "
        f"{c['diagnosis']}": c
        for c in consultations
    }

    selected = st.selectbox(
        "Select Consultation to Monitor",
        list(options)
    )

    consultation = options[selected]

    # -----------------------------------------
    # TREATMENT PLAN
    # -----------------------------------------

    banner(
        "💊 Doctor's Treatment Plan",
        "View the recorded diagnosis, prescription, "
        "and follow-up instructions.",
        "purple"
    )

    a, b = st.columns(2)

    with a:
        st.write(
            "**Doctor:**",
            consultation["doctor_name"]
        )

        st.write(
            "**Diagnosis:**",
            consultation["diagnosis"]
        )

        st.write(
            "**Consultation Date:**",
            consultation["consultation_date"]
        )

    with b:
        st.write(
            "**Prescription:**",
            consultation["prescription"]
        )

        st.write(
            "**Care Instructions:**",
            consultation.get("instructions") or "None"
        )

        st.write(
            "**Next Follow-up:**",
            consultation.get("followup_date") or "None"
        )

    # -----------------------------------------
    # RECOVERY HISTORY
    # -----------------------------------------

    entries = fetch_rows(
        """
        SELECT * FROM recovery_entries
        WHERE patient_id=? AND consultation_id=?
        ORDER BY entry_date, id
        """,
        (patient_id, consultation["id"])
    )

    baseline = consultation.get("baseline_pain")

    latest = entries[-1] if entries else None

    st.subheader("📊 Patient Progress Overview")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "Initial Pain",
        f"{baseline}/10"
        if baseline is not None
        else "Not recorded"
    )

    m2.metric(
        "Latest Pain",
        f"{latest['pain_score']}/10"
        if latest
        else "Not recorded"
    )

    m3.metric(
        "Follow-up Updates",
        len(entries)
    )

    m4.metric(
        "Last Update",
        latest["entry_date"]
        if latest
        else "None"
    )

    # -----------------------------------------
    # SYMPTOM IMPROVEMENT
    # -----------------------------------------

    if latest and baseline is not None:

        improvement = baseline - latest["pain_score"]

        if improvement > 0:
            st.success(
                f"📉 Patient-reported pain decreased "
                f"by {improvement} point(s), "
                f"from {baseline}/10 to "
                f"{latest['pain_score']}/10."
            )

        elif improvement < 0:
            st.warning(
                f"📈 Patient-reported pain increased "
                f"by {abs(improvement)} point(s). "
                "Consult the treating doctor."
            )

        else:
            st.info(
                "The reported pain score has not changed."
            )

        st.caption(
            "A change in pain score indicates a symptom "
            "trend, not medically confirmed recovery."
        )

    elif not entries:
        st.info(
            "No recovery updates yet. Enter the first "
            "follow-up reading below."
        )

    # -----------------------------------------
    # IMPROVEMENT CHART
    # -----------------------------------------

    if entries:

        chart_data = []

        if baseline is not None:
            chart_data.append({
                "Date": (
                    consultation["consultation_date"]
                    + " (baseline)"
                ),
                "Pain Score": baseline
            })

        for entry in entries:
            chart_data.append({
                "Date": (
                    entry["entry_date"]
                    + f" (#{entry['id']})"
                ),
                "Pain Score": entry["pain_score"]
            })

        st.subheader("📉 Symptom Improvement Graph")

        df = pd.DataFrame(chart_data)

        st.line_chart(
            df.set_index("Date"),
            y_label="Pain Score (0–10)"
        )

        st.subheader("📋 Recovery History")

        history_df = pd.DataFrame(entries)

        display_columns = [
            "entry_date",
            "pain_score",
            "symptoms",
            "adherence",
            "heart_rate",
            "systolic",
            "diastolic",
            "oxygen",
            "temperature",
            "patient_notes"
        ]

        st.dataframe(
            history_df[display_columns],
            use_container_width=True,
            hide_index=True
        )

        # Health alerts use entered readings only.

        if latest["pain_score"] >= 8:
            st.warning(
                "High pain score recorded. "
                "Contact the treating clinician."
            )

        if (
            latest.get("oxygen") is not None
            and latest["oxygen"] < 92
        ):
            st.error(
                "Low oxygen saturation recorded. "
                "Seek urgent medical assessment."
            )

    # -----------------------------------------
    # ADD DAILY HEALTH UPDATE
    # -----------------------------------------

    banner(
        "➕ Add Patient Recovery Update",
        "Enter current symptoms, pain score, treatment "
        "adherence, and any measurements actually taken."
    )

    with st.form(
        f"recovery_form_{consultation['id']}",
        clear_on_submit=True
    ):

        entry_date = st.date_input(
            "Follow-up Date",
            value=date.today(),
            min_value=date.fromisoformat(
                consultation["consultation_date"]
            ),
            max_value=date.today()
        )

        pain = st.slider(
            "Current Pain / Symptom Severity (0–10)",
            0, 10, 5
        )

        symptoms = st.text_area(
            "Current Symptoms / Improvements",
            placeholder=(
                "Describe how the patient feels today"
            )
        )

        adherence = st.selectbox(
            "Treatment Adherence",
            [
                "Following the doctor's plan",
                "Partially following",
                "Not following",
                "Not applicable / no medication"
            ]
        )

        st.subheader("Optional Vital Signs")

        st.caption(
            "Only enter measurements that were "
            "actually taken."
        )

        has_hr = st.checkbox(
            "Heart Rate Measured"
        )

        heart_rate = st.number_input(
            "Heart Rate (bpm)",
            min_value=20,
            max_value=250,
            value=75,
            disabled=not has_hr
        )

        has_bp = st.checkbox(
            "Blood Pressure Measured"
        )

        systolic = st.number_input(
            "Systolic BP (mmHg)",
            min_value=50,
            max_value=260,
            value=120,
            disabled=not has_bp
        )

        diastolic = st.number_input(
            "Diastolic BP (mmHg)",
            min_value=30,
            max_value=180,
            value=80,
            disabled=not has_bp
        )

        has_oxygen = st.checkbox(
            "Oxygen Saturation Measured"
        )

        oxygen = st.number_input(
            "SpO₂ (%)",
            min_value=50.0,
            max_value=100.0,
            value=98.0,
            step=0.5,
            disabled=not has_oxygen
        )

        has_temp = st.checkbox(
            "Temperature Measured"
        )

        temperature = st.number_input(
            "Temperature (°C)",
            min_value=30.0,
            max_value=45.0,
            value=37.0,
            step=0.1,
            disabled=not has_temp
        )

        notes = st.text_area(
            "Additional Patient Notes"
        )

        save = st.form_submit_button(
            "💾 Save Recovery Update",
            type="primary",
            use_container_width=True
        )

    if save:

        if not symptoms.strip():
            st.error(
                "Describe the patient's current symptoms."
            )

        else:
            try:
                with get_connection() as conn:

                    conn.execute(
                        """
                        INSERT INTO recovery_entries (
                            patient_id,
                            consultation_id,
                            entry_date,
                            pain_score,
                            symptoms,
                            adherence,
                            heart_rate,
                            systolic,
                            diastolic,
                            oxygen,
                            temperature,
                            patient_notes
                        )
                        VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                        """,
                        (
                            patient_id,
                            consultation["id"],
                            str(entry_date),
                            pain,
                            symptoms.strip(),
                            adherence,
                            heart_rate if has_hr else None,
                            systolic if has_bp else None,
                            diastolic if has_bp else None,
                            oxygen if has_oxygen else None,
                            temperature if has_temp else None,
                            notes.strip()
                        )
                    )

                    conn.commit()

                notify(
                    "Patient recovery update saved successfully! "
                    "Health progress has been refreshed."
                )

            except Exception as exc:
                st.error(
                    f"Could not save recovery update: {exc}"
                )

    st.caption(
        "Health trends are based on entered measurements "
        "and patient-reported symptoms. They do not "
        "establish a diagnosis or confirm recovery."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "MediFlow AI · Patient Management · "
    "Doctor Consultation · Google Health Search · "
    "Patient Recovery Monitoring · Streamlit"
)
