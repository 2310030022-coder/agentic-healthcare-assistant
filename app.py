
import streamlit as st
import pandas as pd
from urllib.parse import quote_plus

from healthcare.database import initialize_database, get_connection
from healthcare.records import (
    get_patients,
    get_patient,
    get_medical_history,
    add_medical_record,
    update_medical_record,
    generate_history_context,
)
from healthcare.appointments import (
    get_doctors,
    get_available_slots,
    book_appointment,
    get_patient_appointments,
    cancel_appointment,
)

# ======================================================
# PAGE SETUP
# ======================================================

st.set_page_config(
    page_title="MediFlow AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()

# ======================================================
# WEBSITE DESIGN
# ======================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg, #eff7ff, #f7f1ff);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #173372, #176b9b);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: white !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #132a4b !important;
    -webkit-text-fill-color: #132a4b !important;
}

section[data-testid="stSidebar"] .stButton button {
    background: white !important;
    color: #173372 !important;
}

.stButton > button {
    border-radius: 12px;
    min-height: 44px;
    font-weight: 700;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #1766e9, #7747e7);
    color: white;
    border: none;
}

[data-testid="stMetric"],
[data-testid="stForm"] {
    background: white;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #dce6f5;
}

.hero {
    background: linear-gradient(100deg, #1765dc, #6745d6);
    padding: 24px;
    border-radius: 20px;
    margin-bottom: 22px;
}

.hero h1,
.hero p {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# DOCTOR PHOTOS
# Shown only when a doctor is selected for booking.
# These are illustrative photographs.
# ======================================================

DOCTOR_IMAGES = {
    "Dr. Kavya Reddy":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=350&fit=crop",
    "Dr. Arjun Nair":
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=350&fit=crop",
    "Dr. Sneha Kapoor":
        "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=350&fit=crop",
    "Dr. Rohan Desai":
        "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=350&fit=crop",
    "Dr. Ishita Verma":
        "https://images.unsplash.com/photo-1591604021695-0c69b7c05981?w=350&fit=crop",
    "Dr. Aditya Menon":
        "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=350&fit=crop",
}

DEFAULT_IMAGE = (
    "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=350&fit=crop"
)

# ======================================================
# DOCTOR DIRECTORY
# ======================================================

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
        (row["name"], row["specialization"])
        for row in conn.execute(
            "SELECT name, specialization FROM doctors"
        )
    }

    for name, specialization in DOCTOR_DATA:
        if (name, specialization) not in existing:
            conn.execute(
                """
                INSERT INTO doctors (name, specialization)
                VALUES (?, ?)
                """,
                (name, specialization),
            )

    conn.commit()

# ======================================================
# DEPARTMENT MATCHING
# ======================================================

DEPARTMENT_KEYWORDS = {
    "Nephrology": [
        "kidney", "renal", "urinary", "bladder"
    ],
    "Cardiology": [
        "heart", "cardiac", "palpitation"
    ],
    "Neurology": [
        "brain", "headache", "migraine", "nerve"
    ],
    "Orthopedics": [
        "bone", "joint", "fracture", "knee"
    ],
    "Dermatology": [
        "skin", "hair", "rash", "acne"
    ],
    "Gastroenterology": [
        "stomach", "digestive", "gastric"
    ],
    "Endocrinology": [
        "diabetes", "thyroid", "hormone"
    ],
    "Pulmonology": [
        "lung", "breathing", "asthma"
    ],
    "Ophthalmology": [
        "eye", "vision"
    ],
    "ENT": [
        "ear", "nose", "throat"
    ],
    "Gynecology": [
        "menstrual", "pregnancy", "gynecology"
    ],
    "Psychiatry": [
        "anxiety", "depression", "psychiatry"
    ],
    "Pediatrics": [
        "child", "pediatric"
    ],
}

# ======================================================
# HELPER FUNCTIONS
# ======================================================

def rows(data):
    return [dict(item) for item in (data or [])]


def show_table(data):
    data = rows(data)

    if data:
        st.dataframe(
            pd.DataFrame(data),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No records available yet.")


def go(destination):
    st.session_state["next_page"] = destination
    st.rerun()


def notify(message):
    st.session_state["notice"] = message
    st.rerun()


def successful(result):
    if isinstance(result, dict):
        return result.get("success", True)

    return result is not False


def google_url(query):
    return (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )


def department_for(query):
    text = str(query).lower()

    for department, keywords in DEPARTMENT_KEYWORDS.items():
        if any(word in text for word in keywords):
            return department

    return "General Medicine"


# ======================================================
# NAVIGATION
# ======================================================

PAGES = [
    "🏠 Dashboard",
    "👤 Patients",
    "📅 Appointments",
    "📋 Medical Records",
    "🩺 History Summary",
    "🔎 Medical Research",
    "🔍 Google Health Assistant",
    "🧠 FAISS Memory",
    "📊 Monitoring",
]

if "next_page" in st.session_state:
    st.session_state["page"] = (
        st.session_state.pop("next_page")
    )

# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.title("🏥 MediFlow AI")
    st.markdown("**HEALTHCARE WORKSPACE**")

    page = st.radio(
        "Modules",
        PAGES,
        key="page",
    )

    st.divider()
    st.subheader("Patient Workspace")

    patients = rows(get_patients())

    patient_options = {
        f"{p['name']} · ID {p['id']}": p["id"]
        for p in patients
    }

    if patient_options:
        selected_patient = st.selectbox(
            "Select patient",
            list(patient_options),
            key="patient_choice",
        )

        patient_id = patient_options[selected_patient]

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
        st.info("Register a patient to begin.")

    if st.button(
        "➕ Register Patient",
        use_container_width=True,
    ):
        go("👤 Patients")

# ======================================================
# SUCCESS NOTIFICATIONS
# ======================================================

if "notice" in st.session_state:
    message = st.session_state.pop("notice")

    st.success(message, icon="✅")
    st.toast(message, icon="🎉")

# ======================================================
# MAIN HEADER
# ======================================================

st.markdown(
    '<div class="hero">'
    '<h1>🏥 MediFlow AI</h1>'
    '<p>Patient Management · Appointments · '
    'Medical Records · Google Health Search</p>'
    '</div>',
    unsafe_allow_html=True,
)

# ======================================================
# DASHBOARD
# ======================================================

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
        len({
            doctor["specialization"]
            for doctor in doctors
        }),
    )

    d.metric(
        "Patient Appointments",
        len(appointments),
    )

    st.subheader("Explore the Platform")

    modules = [
        ("👤 Patients", "👤 Patients"),
        ("📅 Appointments", "📅 Appointments"),
        ("📋 Records", "📋 Medical Records"),
        ("🔍 Health Search", "🔍 Google Health Assistant"),
    ]

    for col, (label, destination) in zip(
        st.columns(4),
        modules,
    ):
        with col:
            with st.container(border=True):
                st.subheader(label)

                if st.button(
                    "Open",
                    key=f"dashboard_{destination}",
                    use_container_width=True,
                ):
                    go(destination)

    st.subheader("Recent Appointments")
    show_table(appointments[:5])

# ======================================================
# PATIENT REGISTRATION
# ======================================================

elif page == "👤 Patients":

    st.header("👤 Patient Registration")

    with st.form(
        "registration",
        clear_on_submit=True,
    ):
        name = st.text_input(
            "Full Patient Name"
        )

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=30,
        )

        submitted = st.form_submit_button(
            "✅ Register Patient",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if len(name.strip()) < 2:
            st.error("Please enter a valid name.")
        else:
            try:
                with get_connection() as conn:
                    cursor = conn.execute(
                        """
                        INSERT INTO patients (name, age)
                        VALUES (?, ?)
                        """,
                        (name.strip(), int(age)),
                    )

                    conn.commit()
                    new_id = cursor.lastrowid

                notify(
                    f"Patient {name.strip()} registered "
                    f"successfully! ID: {new_id}"
                )

            except Exception as exc:
                st.error(
                    f"Registration failed: {exc}"
                )

    st.subheader("Registered Patients")
    show_table(get_patients())

# ======================================================
# APPOINTMENT BOOKING
# ======================================================

elif page == "📅 Appointments":

    st.header("📅 Smart Appointment Booking")

    if not patient_id:
        st.warning(
            "Register and select a patient first."
        )
        st.stop()

    st.write(f"**Patient:** {patient['name']}")

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
        "General consultation": "General Medicine",
    }

    concern = st.selectbox(
        "Step 1 — Consultation type",
        list(guide),
    )

    st.info(
        f"Suggested department: **{guide[concern]}** "
        "(not a diagnosis)"
    )

    doctors = rows(get_doctors())

    departments = sorted({
        doctor["specialization"]
        for doctor in doctors
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
        key=f"dept_{concern}",
    )

    filtered = [
        doctor
        for doctor in doctors
        if doctor["specialization"] == department
    ]

    if not filtered:
        st.warning("No doctors in this department.")
        st.stop()

    doctor_labels = {
        f"{doctor['name']} · {department}": doctor["id"]
        for doctor in filtered
    }

    chosen = st.selectbox(
        "Step 3 — Doctor",
        list(doctor_labels),
        key=f"doctor_{department}",
    )

    doctor_id = doctor_labels[chosen]

    doctor = next(
        doctor
        for doctor in filtered
        if doctor["id"] == doctor_id
    )

    # Doctor photo appears only after selecting a doctor.

    with st.container(border=True):
        photo_col, details_col = st.columns([1, 3])

        with photo_col:
            st.image(
                DOCTOR_IMAGES.get(
                    doctor["name"],
                    DEFAULT_IMAGE,
                ),
                width=170,
            )

        with details_col:
            st.subheader(doctor["name"])

            st.write(
                f"**Department:** {department}"
            )

            st.write(
                f"**Patient:** {patient['name']}"
            )

            st.caption(
                "Illustrative profile photo · "
                "Simulated booking"
            )

    try:
        slots = list(
            get_available_slots(
                doctor_id,
                days=7,
            )
        )

    except Exception as exc:
        slots = []
        st.error(
            f"Could not load slots: {exc}"
        )

    if slots:
        slot = st.selectbox(
            "Step 4 — Available slot",
            slots,
            key=f"slot_{doctor_id}",
        )

        confirm = st.checkbox(
            "I confirm this appointment",
            key=f"confirm_{doctor_id}_{slot}",
        )

        if st.button(
            "✅ Confirm Booking",
            type="primary",
            disabled=not confirm,
            use_container_width=True,
        ):
            try:
                result = book_appointment(
                    patient_id,
                    doctor_id,
                    slot,
                )

                if successful(result):
                    notify(
                        "Appointment booked successfully "
                        f"with {doctor['name']} on {slot}!"
                    )
                else:
                    st.error(
                        result.get(
                            "message",
                            "Booking failed.",
                        )
                    )

            except Exception as exc:
                st.error(
                    f"Booking failed: {exc}"
                )

    else:
        st.warning(
            "No slots are currently available "
            "for this doctor."
        )

    st.subheader("Appointment History")

    appointments = rows(
        get_patient_appointments(patient_id)
    )

    show_table(appointments)

    active = [
        appointment
        for appointment in appointments
        if str(
            appointment.get("status", "")
        ).lower() == "booked"
    ]

    if active:
        cancellation_options = {
            f"#{a['id']} · {a['appointment_time']}": a["id"]
            for a in active
        }

        selected_cancel = st.selectbox(
            "Select appointment to cancel",
            list(cancellation_options),
        )

        if st.button("Cancel Selected Appointment"):
            try:
                result = cancel_appointment(
                    cancellation_options[selected_cancel]
                )

                if successful(result):
                    notify(
                        "Appointment cancelled successfully."
                    )
                else:
                    st.error(
                        result.get(
                            "message",
                            "Cancellation failed.",
                        )
                    )

            except Exception as exc:
                st.error(
                    f"Cancellation failed: {exc}"
                )

# ======================================================
# MEDICAL RECORDS
# ======================================================

elif page == "📋 Medical Records":

    st.header("📋 Medical Records")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    records = rows(
        get_medical_history(patient_id)
    )

    show_table(records)

    st.subheader("Add Medical Record")

    with st.form("add_record"):
        diagnosis = st.text_input(
            "Diagnosis or condition"
        )

        treatment = st.text_area(
            "Treatment"
        )

        notes = st.text_area(
            "Notes"
        )

        save = st.form_submit_button(
            "💾 Save Record",
            type="primary",
        )

    if save:
        if not diagnosis.strip():
            st.error(
                "Enter a diagnosis or condition."
            )
        else:
            try:
                add_medical_record(
                    patient_id,
                    diagnosis.strip(),
                    treatment,
                    notes,
                )

                notify(
                    "Medical record saved successfully."
                )

            except Exception as exc:
                st.error(
                    f"Save failed: {exc}"
                )

    if records:
        st.subheader("Update Existing Record")

        choices = {
            f"#{r['id']} · {r['diagnosis']}": r
            for r in records
        }

        selected = st.selectbox(
            "Select record",
            list(choices),
        )

        record = choices[selected]

        with st.form("edit_record"):
            new_diagnosis = st.text_input(
                "Update diagnosis",
                value=record.get("diagnosis") or "",
            )

            new_treatment = st.text_area(
                "Update treatment",
                value=record.get("treatment") or "",
            )

            new_notes = st.text_area(
                "Update notes",
                value=record.get("notes") or "",
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
                    new_notes,
                )

                notify(
                    "Medical record updated successfully."
                )

            except Exception as exc:
                st.error(
                    f"Update failed: {exc}"
                )

# ======================================================
# HISTORY SUMMARY WITHOUT GEMINI
# ======================================================

elif page == "🩺 History Summary":

    st.header("🩺 Patient History Summary")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    records = rows(
        get_medical_history(patient_id)
    )

    show_table(records)

    if st.button(
        "📋 Generate Records-Based Summary",
        type="primary",
    ):
        try:
            context = generate_history_context(
                patient_id
            )

            st.session_state["history_summary"] = {
                "id": patient_id,
                "text": (
                    str(context)
                    if context
                    else "No patient history available."
                ),
            }

            st.toast(
                "History summary prepared!",
                icon="✅",
            )

        except Exception as exc:
            st.error(
                f"History retrieval failed: {exc}"
            )

    saved = st.session_state.get(
        "history_summary"
    )

    if saved and saved["id"] == patient_id:
        st.subheader("Patient History")

        st.write(saved["text"])

        st.caption(
            "Summary from stored records; "
            "not generated by AI."
        )

# ======================================================
# GOOGLE MEDICAL RESEARCH
# ======================================================

elif page == "🔎 Medical Research":

    st.header("🔎 Medical Research via Google")

    topic = st.text_input(
        "Medical topic",
        placeholder="e.g. chronic kidney disease",
    )

    if topic.strip():
        st.link_button(
            "🔍 Search Google",
            google_url(
                topic + " health information"
            ),
            use_container_width=True,
        )

        st.subheader("Trusted-source searches")

        trusted_sources = [
            ("MedlinePlus", "medlineplus.gov"),
            ("WHO", "who.int"),
            ("NHS", "nhs.uk"),
            ("CDC", "cdc.gov"),
        ]

        for title, domain in trusted_sources:
            st.link_button(
                f"Search {title}",
                google_url(
                    f"site:{domain} {topic}"
                ),
            )

    else:
        st.info(
            "Enter a topic to search Google and "
            "established health-information websites."
        )

    st.caption(
        "Search links open external websites; "
        "their content has not been checked "
        "or summarized by this app."
    )

# ======================================================
# GOOGLE HEALTHCARE ASSISTANT
# ======================================================

elif page == "🔍 Google Health Assistant":

    st.header(
        "🔍 Google-Powered Healthcare Assistant"
    )

    st.caption(
        "Uses saved patient records, doctor information, "
        "and Google Search links. No Gemini API is used."
    )

    query = st.text_area(
        "Describe your request",
        value=(
            "Summarize patient medical history, "
            "find a nephrologist, and research "
            "chronic kidney disease."
        ),
        height=130,
    )

    if st.button(
        "🔍 Process Healthcare Request",
        type="primary",
        use_container_width=True,
    ):
        if not query.strip():
            st.warning("Enter a request first.")

        else:
            department = department_for(query)

            history = (
                "No patient selected or "
                "no history available."
            )

            if patient_id:
                try:
                    history = str(
                        generate_history_context(
                            patient_id
                        )
                        or "No records available."
                    )
                except Exception:
                    history = (
                        "Patient history could "
                        "not be retrieved."
                    )

            matching_doctors = [
                doctor
                for doctor in rows(get_doctors())
                if doctor["specialization"] == department
            ]

            doctor_details = []

            for doctor in matching_doctors[:5]:
                try:
                    slots = list(
                        get_available_slots(
                            doctor["id"],
                            days=7,
                        )
                    )[:3]

                except Exception:
                    slots = []

                doctor_details.append({
                    "name": doctor["name"],
                    "specialization": department,
                    "slots": slots,
                })

            st.session_state["google_result"] = {
                "query": query,
                "patient_id": patient_id,
                "department": department,
                "history": history,
                "doctors": doctor_details,
            }

            st.toast(
                "Request processed successfully!",
                icon="✅",
            )

    result = st.session_state.get(
        "google_result"
    )

    if (
        result
        and result["patient_id"] == patient_id
    ):
        st.success(
            "Patient and doctor information retrieved."
        )

        st.subheader("Request Overview")
        st.write(result["query"])

        st.subheader("Suggested Department")
        st.write(result["department"])

        st.caption(
            "Keyword-based routing only; "
            "not a medical diagnosis."
        )

        st.subheader("Patient History")
        st.write(result["history"])

        st.subheader("Matching Doctors")

        if result["doctors"]:
            for doctor in result["doctors"]:
                with st.container(border=True):
                    st.write(
                        f"**{doctor['name']}** · "
                        f"{doctor['specialization']}"
                    )

                    slots = doctor["slots"]

                    st.write(
                        "Slots: "
                        + (
                            ", ".join(map(str, slots))
                            if slots
                            else "None returned"
                        )
                    )
        else:
            st.info("No matching doctors found.")

        st.subheader("Google Health Research")

        # Search only the topic rather than sending
        # saved patient records to Google.
        search_query = (
            result["department"]
            + " health information"
        )

        st.link_button(
            "🔍 Search Google",
            google_url(search_query),
            use_container_width=True,
        )

        st.link_button(
            "Search MedlinePlus",
            google_url(
                "site:medlineplus.gov "
                + search_query
            ),
        )

        st.link_button(
            "Search WHO",
            google_url(
                "site:who.int "
                + search_query
            ),
        )

        if st.button(
            "📅 Open Appointment Booking"
        ):
            go("📅 Appointments")

        st.caption(
            "Google links use the medical topic, "
            "not the saved patient history."
        )

# ======================================================
# FAISS MEMORY
# ======================================================

elif page == "🧠 FAISS Memory":

    st.header("🧠 Patient Semantic Memory")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    query = st.text_input(
        "Search patient records by meaning"
    )

    if st.button(
        "🔍 Search Memory",
        type="primary",
    ):
        if not query.strip():
            st.warning("Enter a search query.")

        else:
            try:
                from healthcare.memory import (
                    retrieve_patient_memory,
                )

                matches = retrieve_patient_memory(
                    patient_id,
                    query,
                )

                if not matches:
                    st.info("No matching memory found.")

                for index, item in enumerate(
                    matches, 1
                ):
                    with st.container(border=True):
                        st.subheader(
                            f"Match {index}"
                        )

                        st.write(
                            item.get("content", "")
                        )

                        similarity = float(
                            item.get(
                                "similarity", 0
                            )
                        )

                        st.caption(
                            f"Similarity: {similarity:.3f}"
                        )

            except Exception as exc:
                st.error(
                    f"Memory search failed: {exc}"
                )

# ======================================================
# MONITORING
# ======================================================

elif page == "📊 Monitoring":

    st.header("📊 Monitoring and Evaluation")

    try:
        from healthcare.monitoring import (
            get_agent_logs,
            get_monitoring_metrics,
        )

        st.subheader("Monitoring Metrics")

        st.json(
            get_monitoring_metrics()
        )

        st.subheader("Execution Logs")

        show_table(
            get_agent_logs(limit=100)
        )

    except Exception as exc:
        st.info(
            f"Monitoring unavailable: {exc}"
        )

    try:
        from healthcare.evaluation import (
            get_evaluation_metrics,
        )

        st.subheader("Evaluation Metrics")

        st.json(
            get_evaluation_metrics()
        )

    except Exception as exc:
        st.info(
            f"Evaluation unavailable: {exc}"
        )

# ======================================================
# FOOTER
# ======================================================

st.divider()

st.caption(
    "MediFlow AI · Patient Management · "
    "Google Health Search · FAISS · Streamlit"
)
