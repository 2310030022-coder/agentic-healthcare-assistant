
import streamlit as st
import pandas as pd

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
from healthcare.medical_search import retrieve_medical_information
from healthcare.config import generate_ai_response


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
# PROFESSIONAL WEBSITE DESIGN
# ======================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(115deg, #f0f8ff, #f7f0ff);
    color: #142448;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #192a69, #176c9d);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: white !important;
}

section[data-testid="stSidebar"] [role="radiogroup"] p {
    color: white !important;
    font-size: 16px !important;
    font-weight: 700 !important;
}

section[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #142448 !important;
    -webkit-text-fill-color: #142448 !important;
}

section[data-testid="stSidebar"] .stButton button {
    background: white !important;
    color: #153d82 !important;
    border: 2px solid #b8d7ff !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] .stButton button p {
    color: #153d82 !important;
}

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 45px;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #1768e8, #7743e8);
    border: none;
    color: white;
}

[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 16px;
    border: 1px solid #dbe5fa;
}

[data-testid="stForm"] {
    background: white;
    padding: 18px;
    border-radius: 18px;
    border: 1px solid #dce6f8;
}

h1, h2, h3 {
    color: #193b78;
    font-weight: 800;
}

.hero {
    background: linear-gradient(110deg, #125ad7, #6844d8);
    color: white;
    padding: 30px;
    border-radius: 22px;
    margin: 14px 0 25px;
}

.hero h1, .hero p {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# ======================================================
# DOCTOR IMAGES
# Illustrative photos, not images of named doctors.
# ======================================================

DOCTOR_IMAGES = {
    "Nephrology":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=450&fit=crop",
    "Cardiology":
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=450&fit=crop",
    "General Medicine":
        "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=450&fit=crop",
    "Neurology":
        "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=450&fit=crop",
    "Orthopedics":
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=450&fit=crop",
    "Dermatology":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=450&fit=crop",
}

DEFAULT_IMAGE = (
    "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=450&fit=crop"
)


# ======================================================
# ADD DOCTORS ACROSS DEPARTMENTS
# ======================================================

EXTRA_DOCTORS = [
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

    for name, specialization in EXTRA_DOCTORS:
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
# HELPER FUNCTIONS
# ======================================================

def table(items):
    if items:
        st.dataframe(
            pd.DataFrame([dict(x) for x in items]),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.info("No entries yet.")


def go(destination):
    st.session_state["next_page"] = destination
    st.rerun()


def announce(message):
    st.session_state["notice"] = message
    st.rerun()


def successful(result):
    if isinstance(result, dict):
        return result.get("success", True)
    return result is not False


# ======================================================
# NAVIGATION
# ======================================================

PAGES = [
    "🏠 Dashboard",
    "👤 Patients",
    "👨‍⚕️ Doctors",
    "📅 Appointments",
    "📋 Medical Records",
    "🩺 History Summary",
    "🔎 Medical Research",
    "🤖 AI Assistant",
    "🧠 FAISS Memory",
    "📊 Monitoring",
]

if "next_page" in st.session_state:
    st.session_state["page"] = st.session_state.pop(
        "next_page"
    )


# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.title("🏥 MediFlow AI")
    st.markdown("**HEALTHCARE WORKSPACE**")

    page = st.radio(
        "Explore modules",
        PAGES,
        key="page",
    )

    st.divider()
    st.subheader("Patient Workspace")

    patients = [dict(x) for x in get_patients()]

    labels = {
        f"{x['name']} · ID {x['id']}": x["id"]
        for x in patients
    }

    chosen = (
        st.selectbox(
            "Select patient",
            list(labels),
            key="patient_choice",
        )
        if labels
        else None
    )

    patient_id = labels[chosen] if chosen else None

    patient = (
        dict(get_patient(patient_id))
        if patient_id is not None
        else None
    )

    if patient:
        st.write(
            f"**{patient['name']}** · {patient['age']} years"
        )

    if st.button(
        "➕ Register New Patient",
        use_container_width=True,
    ):
        go("👤 Patients")


# ======================================================
# SUCCESS ALERTS AND POPUP NOTIFICATIONS
# ======================================================

if "notice" in st.session_state:
    notice = st.session_state.pop("notice")

    st.success(notice, icon="✅")
    st.toast(notice, icon="🎉")


# ======================================================
# WEBSITE HEADER
# ======================================================

st.markdown(
    """
    <div class="hero">
        <h1>🏥 MediFlow AI</h1>
        <p>
            Smart Patient Management · Doctor Discovery ·
            Appointments · AI-Powered Assistance
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ======================================================
# DASHBOARD
# ======================================================

if page == "🏠 Dashboard":

    doctors = [dict(x) for x in get_doctors()]

    bookings = (
        [
            dict(x)
            for x in get_patient_appointments(patient_id)
        ]
        if patient_id
        else []
    )

    cols = st.columns(4)

    labels = [
        "Patients",
        "Doctors",
        "Patient Appointments",
        "Departments",
    ]

    values = [
        len(patients),
        len(doctors),
        len(bookings),
        len({
            d["specialization"]
            for d in doctors
        }),
    ]

    for col, label, value in zip(
        cols, labels, values
    ):
        col.metric(label, value)

    st.subheader("Explore the Platform")

    options = [
        ("🤖 Intelligent AI Agent", "🤖 AI Assistant"),
        ("📅 Smart Appointments", "📅 Appointments"),
        ("👨‍⚕️ Browse Doctors", "👨‍⚕️ Doctors"),
        ("🧠 Semantic Memory", "🧠 FAISS Memory"),
    ]

    for col, (label, target) in zip(
        st.columns(4), options
    ):
        with col:
            with st.container(border=True):
                st.markdown("### " + label)

                if st.button(
                    "Open Module →",
                    key="nav_" + target,
                    use_container_width=True,
                ):
                    go(target)

    st.subheader("👨‍⚕️ Featured Doctors")

    for col, doctor in zip(
        st.columns(3), doctors[:3]
    ):
        with col:
            with st.container(border=True):

                st.image(
                    DOCTOR_IMAGES.get(
                        doctor["specialization"],
                        DEFAULT_IMAGE,
                    ),
                    use_container_width=True,
                )

                st.markdown(
                    "**" + doctor["name"] + "**"
                )

                st.caption(
                    doctor["specialization"]
                    + " · Illustrative profile photo"
                )

                if st.button(
                    "Book With This Doctor",
                    key="home_dr_" + str(doctor["id"]),
                    use_container_width=True,
                ):
                    st.session_state["pref_doctor"] = (
                        doctor["id"]
                    )
                    go("📅 Appointments")

    st.subheader("Recent Appointments")
    table(bookings[:5])


# ======================================================
# PATIENT REGISTRATION
# ======================================================

elif page == "👤 Patients":

    st.header("👤 Register a Patient")

    with st.form(
        "register",
        clear_on_submit=True,
    ):
        name = st.text_input(
            "Full Patient Name",
            placeholder="Enter full name",
        )

        age = st.number_input(
            "Age",
            min_value=0,
            max_value=120,
            value=30,
        )

        submit = st.form_submit_button(
            "➕ Register Patient",
            type="primary",
            use_container_width=True,
        )

    if submit:
        if len(name.strip()) < 2:
            st.error(
                "Please enter a valid patient name."
            )
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

                announce(
                    f"Patient {name.strip()} registered "
                    f"successfully! Patient ID: {new_id}"
                )

            except Exception as exc:
                st.error(
                    f"Registration failed: {exc}"
                )

    st.subheader("Registered Patients")
    table(get_patients())


# ======================================================
# DOCTORS DIRECTORY
# ======================================================

elif page == "👨‍⚕️ Doctors":

    st.header("👨‍⚕️ Meet Our Doctors")

    doctors = [dict(x) for x in get_doctors()]

    specialties = sorted({
        d["specialization"]
        for d in doctors
    })

    selected_specialty = st.selectbox(
        "Filter By Department",
        ["All Departments"] + specialties,
    )

    shown = [
        d for d in doctors
        if (
            selected_specialty == "All Departments"
            or d["specialization"] == selected_specialty
        )
    ]

    for offset in range(0, len(shown), 3):

        for col, doctor in zip(
            st.columns(3),
            shown[offset:offset + 3],
        ):

            with col:
                with st.container(border=True):

                    st.image(
                        DOCTOR_IMAGES.get(
                            doctor["specialization"],
                            DEFAULT_IMAGE,
                        ),
                        use_container_width=True,
                    )

                    st.subheader(doctor["name"])

                    st.write(
                        "🩺 " + doctor["specialization"]
                    )

                    st.caption(
                        "Illustrative photo · "
                        "Simulated doctor profile"
                    )

                    if st.button(
                        "📅 Book Appointment",
                        key="doctor_" + str(doctor["id"]),
                        use_container_width=True,
                    ):
                        st.session_state["pref_doctor"] = (
                            doctor["id"]
                        )
                        go("📅 Appointments")


# ======================================================
# SMART APPOINTMENT BOOKING
# ======================================================

elif page == "📅 Appointments":

    st.header("📅 Smart Appointment Booking")

    if not patient_id:
        st.warning(
            "Register and select a patient first."
        )
        st.stop()

    st.write(
        "**Patient:** " + patient["name"]
    )

    guide = {
        "Kidney concerns": "Nephrology",
        "Heart concerns": "Cardiology",
        "Headaches or nervous system": "Neurology",
        "Bones or joints": "Orthopedics",
        "Skin or hair": "Dermatology",
        "Digestive concerns": "Gastroenterology",
        "Diabetes or thyroid": "Endocrinology",
        "Breathing concerns": "Pulmonology",
        "Ear, nose or throat": "ENT",
        "Eye or vision": "Ophthalmology",
        "Women's health": "Gynecology",
        "Mental health": "Psychiatry",
        "Children's health": "Pediatrics",
        "General consultation": "General Medicine",
    }

    concern = st.selectbox(
        "What Type of Consultation Do You Need?",
        list(guide),
    )

    st.info(
        "Suggested Department: **"
        + guide[concern]
        + "**. This is a navigation aid, not a diagnosis."
    )

    doctors = [dict(x) for x in get_doctors()]

    specialties = sorted({
        d["specialization"]
        for d in doctors
    })

    preferred_id = st.session_state.pop(
        "pref_doctor",
        None,
    )

    preferred_doctor = next(
        (
            d for d in doctors
            if d["id"] == preferred_id
        ),
        None,
    )

    preferred_specialty = (
        preferred_doctor["specialization"]
        if preferred_doctor
        else guide[concern]
    )

    department = st.selectbox(
        "Select Department",
        specialties,
        index=(
            specialties.index(preferred_specialty)
            if preferred_specialty in specialties
            else 0
        ),
        key=f"booking_department_{concern}_{preferred_id}",
    )

    filtered = [
        d for d in doctors
        if d["specialization"] == department
    ]

    names = {
        f"{d['name']} · {d['specialization']}": d["id"]
        for d in filtered
    }

    options = list(names)

    default_index = next(
        (
            i for i, label in enumerate(options)
            if names[label] == preferred_id
        ),
        0,
    )

    selected = st.selectbox(
        "Select Doctor",
        options,
        index=default_index,
    )

    doctor = next(
        d for d in filtered
        if d["id"] == names[selected]
    )

    with st.container(border=True):

        photo_col, info_col = st.columns([1, 2])

        with photo_col:
            st.image(
                DOCTOR_IMAGES.get(
                    department,
                    DEFAULT_IMAGE,
                ),
                use_container_width=True,
            )

        with info_col:
            st.subheader(doctor["name"])

            st.write(
                "**Department:** " + department
            )

            st.write(
                "**Patient:** " + patient["name"]
            )

            st.caption(
                "Illustrative photo · "
                "Appointment slots are simulated"
            )

    slots = get_available_slots(
        doctor["id"],
        days=7,
    )

    if slots:

        slot = st.selectbox(
            "Available Date and Time",
            slots,
        )

        confirm = st.checkbox(
            "I confirm this appointment selection",
            key="booking_confirm",
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
                    doctor["id"],
                    slot,
                )

                if successful(result):
                    announce(
                        "Appointment booked successfully "
                        f"with {doctor['name']} on {slot}!"
                    )
                else:
                    st.error(
                        result.get(
                            "message",
                            "Unable to book appointment.",
                        )
                    )

            except Exception as exc:
                st.error(
                    "Booking failed: " + str(exc)
                )

    else:
        st.warning(
            "No available slots for this doctor."
        )

    st.subheader("Your Appointments")

    appointments = [
        dict(x)
        for x in get_patient_appointments(patient_id)
    ]

    table(appointments)

    active = [
        a for a in appointments
        if a.get("status") == "Booked"
    ]

    if active:

        cancel_options = {
            f"#{a['id']} · {a['appointment_time']}": a["id"]
            for a in active
        }

        selected_cancel = st.selectbox(
            "Cancel An Appointment",
            list(cancel_options),
        )

        if st.button("Cancel Selected Appointment"):

            result = cancel_appointment(
                cancel_options[selected_cancel]
            )

            if successful(result):
                announce(
                    "Appointment cancelled successfully."
                )
            else:
                st.error(
                    result.get(
                        "message",
                        "Cancellation failed.",
                    )
                )


# ======================================================
# MEDICAL RECORD MANAGEMENT
# ======================================================

elif page == "📋 Medical Records":

    st.header("📋 Medical Records")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    records = [
        dict(r)
        for r in get_medical_history(patient_id)
    ]

    table(records)

    st.subheader("Add Medical Record")

    with st.form("new_record"):

        diagnosis = st.text_input(
            "Diagnosis or Condition"
        )

        treatment = st.text_area(
            "Treatment"
        )

        notes = st.text_area(
            "Notes"
        )

        save = st.form_submit_button(
            "💾 Save Medical Record",
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
                    diagnosis,
                    treatment,
                    notes,
                )

                announce(
                    "Medical record saved successfully."
                )

            except Exception as exc:
                st.error(str(exc))

    if records:

        st.subheader("Update Existing Record")

        choices = {
            f"#{r['id']} · {r['diagnosis']}": r
            for r in records
        }

        selected = st.selectbox(
            "Edit Existing Record",
            list(choices),
        )

        record = choices[selected]

        with st.form("edit_record"):

            new_diagnosis = st.text_input(
                "Update Diagnosis",
                value=record.get("diagnosis") or "",
            )

            new_treatment = st.text_area(
                "Update Treatment",
                value=record.get("treatment") or "",
            )

            new_notes = st.text_area(
                "Update Notes",
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

                announce(
                    "Medical record updated successfully."
                )

            except Exception as exc:
                st.error(str(exc))


# ======================================================
# AI MEDICAL HISTORY SUMMARY
# ======================================================

elif page == "🩺 History Summary":

    st.header("🩺 AI Medical History Summary")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    records = get_medical_history(patient_id)

    table(records)

    if st.button(
        "✨ Generate History Summary",
        type="primary",
        disabled=not bool(records),
    ):

        with st.spinner(
            "Summarizing medical records..."
        ):

            try:
                prompt = (
                    "Summarize ONLY the supplied fictional "
                    "patient history. Do not invent diagnoses, "
                    "details or prescribe.\n\n"
                    + generate_history_context(patient_id)
                )

                summary = generate_ai_response(
                    prompt
                )

                st.session_state["history_summary"] = {
                    "id": patient_id,
                    "text": summary,
                }

                st.toast(
                    "History summary ready!",
                    icon="✅",
                )

            except Exception as exc:
                st.error(
                    "Summary failed: " + str(exc)
                )

    saved = st.session_state.get(
        "history_summary"
    )

    if saved and saved["id"] == patient_id:
        st.write(saved["text"])


# ======================================================
# MEDICAL INFORMATION SEARCH
# ======================================================

elif page == "🔎 Medical Research":

    st.header("🔎 Trusted Medical Information Search")

    query = st.text_input(
        "Medical Topic",
        placeholder="e.g. chronic kidney disease",
    )

    if st.button(
        "🔍 Search Trusted Sources",
        type="primary",
    ):

        if not query.strip():
            st.warning("Enter a topic.")

        else:
            with st.spinner(
                "Searching medical resources..."
            ):

                try:
                    st.session_state["medical_sources"] = (
                        retrieve_medical_information(
                            query
                        )
                    )

                except Exception as exc:
                    st.error(str(exc))

    data = st.session_state.get(
        "medical_sources",
        {},
    )

    for item in data.get("sources", []):

        with st.container(border=True):

            st.subheader(
                item.get(
                    "title",
                    "Medical Information",
                )
            )

            st.write(
                item.get("content", "")
            )

            url = item.get("url", "")

            if (
                url.startswith(
                    "https://medlineplus.gov/"
                )
                or url.startswith(
                    "https://www.medlineplus.gov/"
                )
            ):
                st.link_button(
                    "Read Trusted Source",
                    url,
                )

    if data and not data.get("sources"):
        st.info(
            "No matching verified sources found."
        )


# ======================================================
# AI HEALTHCARE ASSISTANT
# ======================================================

elif page == "🤖 AI Assistant":

    st.header("🤖 AI Healthcare Assistant")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    query = st.text_area(
        "Describe Your Request",
        value=(
            "Summarize patient history, "
            "find a nephrologist, and research "
            "chronic kidney disease."
        ),
        height=130,
    )

    if st.button(
        "✨ Run AI Healthcare Agent",
        type="primary",
    ):

        if not query.strip():
            st.warning("Enter a request.")

        else:
            with st.spinner(
                "Planning and running agent tools..."
            ):

                try:
                    from healthcare.agent import (
                        run_healthcare_agent,
                    )

                    result = run_healthcare_agent(
                        query,
                        patient_id,
                    )

                    st.session_state["agent_output"] = (
                        result
                    )

                    st.toast(
                        "Agent finished!",
                        icon="✅",
                    )

                except Exception as exc:
                    st.error(
                        "Agent failed: " + str(exc)
                    )

    result = st.session_state.get(
        "agent_output"
    )

    if result:

        st.subheader("Agent Response")

        st.write(
            result.get("response", "")
        )

        with st.expander("Agent Plan"):
            st.write(
                result.get("plan", "")
            )

        with st.expander("Execution Trace"):
            st.write(
                result.get(
                    "execution_trace",
                    [],
                )
            )

    if st.button("📅 Open Booking"):
        go("📅 Appointments")


# ======================================================
# FAISS SEMANTIC MEMORY
# ======================================================

elif page == "🧠 FAISS Memory":

    st.header("🧠 Patient Semantic Memory")

    if not patient_id:
        st.warning("Select a patient first.")
        st.stop()

    query = st.text_input(
        "Search Patient History By Meaning"
    )

    if st.button(
        "🔍 Search Memory",
        type="primary",
    ):

        if not query.strip():
            st.warning("Enter a query.")

        else:
            with st.spinner(
                "Searching semantic memory..."
            ):

                try:
                    from healthcare.memory import (
                        retrieve_patient_memory,
                    )

                    matches = retrieve_patient_memory(
                        patient_id,
                        query,
                    )

                    for item in matches:

                        with st.container(border=True):

                            st.write(
                                item.get("content", "")
                            )

                            similarity = float(
                                item.get(
                                    "similarity",
                                    0,
                                )
                            )

                            st.caption(
                                f"Similarity: {similarity:.3f}"
                            )

                    if not matches:
                        st.info(
                            "No matching memory found."
                        )

                except Exception as exc:
                    st.error(
                        "Memory unavailable: " + str(exc)
                    )


# ======================================================
# MONITORING AND EVALUATION
# ======================================================

elif page == "📊 Monitoring":

    st.header("📊 Agent Evaluation and Monitoring")

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

        table(
            get_agent_logs(limit=100)
        )

    except Exception as exc:
        st.warning(
            "Monitoring unavailable: " + str(exc)
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
        st.warning(
            "Evaluation unavailable: " + str(exc)
        )


# ======================================================
# FOOTER
# ======================================================

st.divider()

st.caption(
    "MediFlow AI · Gemini AI · LangGraph · "
    "FAISS · Streamlit"
)
