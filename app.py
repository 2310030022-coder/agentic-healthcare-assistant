
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


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MediFlow AI | Healthcare Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

initialize_database()


# ============================================================
# WEBSITE DESIGN
# ============================================================

st.markdown("""
<style>
.stApp {
    background: linear-gradient(120deg, #f0f7ff, #f7f2ff);
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #172e70, #126f9c);
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
    color: #162a4d !important;
    -webkit-text-fill-color: #162a4d !important;
}

section[data-testid="stSidebar"] .stButton button {
    background: #ffffff !important;
    color: #164181 !important;
    border: 2px solid #b9d6ff !important;
}

section[data-testid="stSidebar"] .stButton button p {
    color: #164181 !important;
}

.stButton > button {
    border-radius: 12px;
    font-weight: 750;
    min-height: 46px;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #1767e8, #7746e8);
    border: none;
    color: white;
}

[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border: 1px solid #dbe5f8;
    border-radius: 15px;
}

[data-testid="stForm"] {
    background: white;
    padding: 18px;
    border: 1px solid #dbe5f8;
    border-radius: 16px;
}

h1, h2, h3 {
    color: #193a78;
}

.hero {
    background: linear-gradient(110deg, #155ed8, #6544d5);
    padding: 26px;
    border-radius: 20px;
    margin-bottom: 22px;
}

.hero h1, .hero p {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# DOCTOR IMAGES
# Each listed doctor has a separate illustrative photo URL.
# Photos are not the actual identities of the named doctors.
# ============================================================

DOCTOR_IMAGES = {
    "Dr. Kavya Reddy":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=320&h=360&fit=crop",
    "Dr. Arjun Nair":
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=320&h=360&fit=crop",
    "Dr. Sneha Kapoor":
        "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=320&h=360&fit=crop",
    "Dr. Rohan Desai":
        "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=320&h=360&fit=crop",
    "Dr. Ishita Verma":
        "https://images.unsplash.com/photo-1591604021695-0c69b7c05981?w=320&h=360&fit=crop",
    "Dr. Aditya Menon":
        "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=320&h=360&fit=crop",
    "Dr. Neha Shah":
        "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=320&h=360&fit=crop",
    "Dr. Vivek Bansal":
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=320&h=360&fit=crop",
    "Dr. Pooja Sinha":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=320&h=360&fit=crop",
    "Dr. Nikhil Joshi":
        "https://images.unsplash.com/photo-1622253692010-333f2da6031d?w=320&h=360&fit=crop",
    "Dr. Ritu Malhotra":
        "https://images.unsplash.com/photo-1591604021695-0c69b7c05981?w=320&h=360&fit=crop",
    "Dr. Aarav Khanna":
        "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=320&h=360&fit=crop",
    "Dr. Diya Sharma":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=320&h=360&fit=crop",
    "Dr. Simran Gupta":
        "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=320&h=360&fit=crop",
}

DEFAULT_IMAGE = (
    "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=320&h=360&fit=crop"
)


# ============================================================
# DOCTOR DATABASE
# ============================================================

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
        (r["name"], r["specialization"])
        for r in conn.execute(
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


# ============================================================
# HELPERS
# ============================================================

def rows_as_dicts(items):
    return [dict(item) for item in items]


def show_table(items):
    if items:
        st.dataframe(
            pd.DataFrame(rows_as_dicts(items)),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No records available.")


def navigate(destination):
    st.session_state["_next_page"] = destination
    st.rerun()


def show_success_after_rerun(message):
    st.session_state["_success_message"] = message
    st.rerun()


def succeeded(result):
    if isinstance(result, dict):
        return result.get("success", True)
    return result is not False


def failure_message(result):
    if isinstance(result, dict):
        return result.get("message", "Operation failed.")
    return "Operation failed."


# ============================================================
# NAVIGATION
# ============================================================

PAGES = [
    "🏠 Dashboard",
    "👤 Patients",
    "📅 Appointments",
    "📋 Medical Records",
    "🩺 History Summary",
    "🔎 Medical Research",
    "🤖 AI Assistant",
    "🧠 FAISS Memory",
    "📊 Monitoring",
]

if "_next_page" in st.session_state:
    st.session_state["current_page"] = (
        st.session_state.pop("_next_page")
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.title("🏥 MediFlow AI")
    st.markdown("**INTELLIGENT HEALTHCARE WORKSPACE**")

    page = st.radio(
        "Explore Modules",
        PAGES,
        key="current_page",
    )

    st.divider()
    st.subheader("👤 Patient Workspace")

    patients = rows_as_dicts(get_patients())

    patient_options = {
        f"{p['name']} · ID {p['id']}": p["id"]
        for p in patients
    }

    if patient_options:
        selected_patient = st.selectbox(
            "Select Patient",
            list(patient_options.keys()),
            key="patient_selector",
        )

        patient_id = patient_options[selected_patient]
        patient_row = get_patient(patient_id)
        patient = dict(patient_row) if patient_row else None

        if patient:
            st.write(f"**Patient:** {patient['name']}")
            st.write(f"**Age:** {patient['age']} years")
    else:
        patient_id = None
        patient = None
        st.warning("No patients registered.")

    if st.button(
        "➕ Register New Patient",
        use_container_width=True,
        key="sidebar_register",
    ):
        navigate("👤 Patients")

    st.divider()
    st.caption("✨ Powered by Google Gemini")


# ============================================================
# SUCCESS ALERTS
# ============================================================

if "_success_message" in st.session_state:
    message = st.session_state.pop("_success_message")

    st.success(message, icon="✅")
    st.toast(message, icon="🎉")


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown("""
<div class="hero">
    <h1>🏥 MediFlow AI</h1>
    <p>
        Smart Patient Management · Appointment Scheduling ·
        Medical Records · AI Healthcare Assistant
    </p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# DASHBOARD — NO DOCTOR IMAGES
# ============================================================

if page == "🏠 Dashboard":

    doctors = rows_as_dicts(get_doctors())

    appointments = (
        rows_as_dicts(get_patient_appointments(patient_id))
        if patient_id is not None
        else []
    )

    departments = {
        doctor["specialization"]
        for doctor in doctors
    }

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Patients", len(patients))
    c2.metric("👨‍⚕️ Doctors", len(doctors))
    c3.metric("🏥 Departments", len(departments))
    c4.metric("📅 Appointments", len(appointments))

    st.subheader("✨ Explore the Platform")

    modules = [
        ("👤 Patient Management", "👤 Patients"),
        ("📅 Book Appointments", "📅 Appointments"),
        ("📋 Medical Records", "📋 Medical Records"),
        ("🤖 AI Healthcare Agent", "🤖 AI Assistant"),
    ]

    for col, (label, target) in zip(
        st.columns(4),
        modules,
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"### {label}")

                if st.button(
                    "Open Module",
                    key=f"module_{target}",
                    use_container_width=True,
                ):
                    navigate(target)

    st.subheader("🚀 Quick Actions")

    quick1, quick2, quick3 = st.columns(3)

    with quick1:
        if st.button(
            "➕ Register Patient",
            use_container_width=True,
        ):
            navigate("👤 Patients")

    with quick2:
        if st.button(
            "📅 Schedule Appointment",
            use_container_width=True,
        ):
            navigate("📅 Appointments")

    with quick3:
        if st.button(
            "📋 Add Medical Record",
            use_container_width=True,
        ):
            navigate("📋 Medical Records")

    st.subheader("📅 Recent Appointments")
    show_table(appointments[:5])


# ============================================================
# PATIENT REGISTRATION
# ============================================================

elif page == "👤 Patients":

    st.header("👤 Patient Registration")

    with st.form(
        "patient_registration",
        clear_on_submit=True,
    ):
        name = st.text_input(
            "Patient Full Name",
            placeholder="Enter full name",
        )

        age = st.number_input(
            "Patient Age",
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
            st.error("Please enter a valid patient name.")
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

                show_success_after_rerun(
                    f"Patient {name.strip()} registered "
                    f"successfully! Patient ID: {new_id}"
                )

            except Exception as exc:
                st.error(f"Registration failed: {exc}")

    st.subheader("👥 Registered Patients")
    show_table(get_patients())


# ============================================================
# APPOINTMENT BOOKING
# ============================================================

elif page == "📅 Appointments":

    st.header("📅 Smart Appointment Booking")

    if patient_id is None:
        st.warning("Register and select a patient first.")
        st.stop()

    st.success(f"Selected Patient: {patient['name']}")

    department_guide = {
        "Kidney or urinary concerns": "Nephrology",
        "Heart concerns": "Cardiology",
        "Neurological concerns": "Neurology",
        "Bones and joints": "Orthopedics",
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

    st.subheader("Step 1 — Choose Consultation Type")

    concern = st.selectbox(
        "Patient Concern",
        list(department_guide.keys()),
    )

    suggested = department_guide[concern]

    st.info(f"Suggested Department: **{suggested}**")

    doctors = rows_as_dicts(get_doctors())

    departments = sorted({
        d["specialization"]
        for d in doctors
    })

    if not departments:
        st.error("No doctors available.")
        st.stop()

    st.subheader("Step 2 — Select Department")

    department = st.selectbox(
        "Medical Department",
        departments,
        index=(
            departments.index(suggested)
            if suggested in departments
            else 0
        ),
        key=f"department_{concern}",
    )

    filtered_doctors = [
        d for d in doctors
        if d["specialization"] == department
    ]

    if not filtered_doctors:
        st.warning("No doctors available in this department.")
        st.stop()

    st.subheader("Step 3 — Select Doctor")

    doctor_options = {
        d["name"] + f" · {d['specialization']}": d["id"]
        for d in filtered_doctors
    }

    selected_doctor_label = st.selectbox(
        "Doctor Name",
        list(doctor_options.keys()),
        key=f"doctor_{department}",
    )

    doctor_id = doctor_options[selected_doctor_label]

    doctor = next(
        d for d in filtered_doctors
        if d["id"] == doctor_id
    )

    # Doctor image appears ONLY here,
    # after department and doctor selection.
    with st.container(border=True):

        photo_col, details_col = st.columns([1, 3])

        with photo_col:
            st.image(
                DOCTOR_IMAGES.get(
                    doctor["name"],
                    DEFAULT_IMAGE,
                ),
                width=175,
            )

        with details_col:
            st.subheader(doctor["name"])

            st.write(
                f"**Specialization:** {department}"
            )

            st.write(
                f"**Patient:** {patient['name']}"
            )

            st.write(
                "**Availability:** Choose a slot below"
            )

            st.caption("Illustrative doctor profile photograph")

    st.subheader("Step 4 — Select Appointment Slot")

    try:
        slots = get_available_slots(
            doctor_id,
            days=7,
        )
    except Exception as exc:
        slots = []
        st.error(f"Unable to retrieve slots: {exc}")

    if slots:
        selected_slot = st.selectbox(
            "Available Date and Time",
            slots,
            key=f"slot_{doctor_id}",
        )

        st.subheader("Step 5 — Confirm Booking")

        with st.container(border=True):
            st.write(f"**Patient:** {patient['name']}")
            st.write(f"**Doctor:** {doctor['name']}")
            st.write(f"**Department:** {department}")
            st.write(f"**Appointment:** {selected_slot}")

            confirm = st.checkbox(
                "I confirm this appointment",
                key=f"confirm_{doctor_id}_{selected_slot}",
            )

            if st.button(
                "✅ Confirm Appointment",
                type="primary",
                disabled=not confirm,
                use_container_width=True,
            ):
                try:
                    result = book_appointment(
                        patient_id,
                        doctor_id,
                        selected_slot,
                    )

                    if succeeded(result):
                        show_success_after_rerun(
                            "Appointment booked successfully! "
                            f"Doctor: {doctor['name']} | "
                            f"Time: {selected_slot}"
                        )
                    else:
                        st.error(failure_message(result))

                except Exception as exc:
                    st.error(f"Booking failed: {exc}")

    else:
        st.warning(
            "No available appointment slots for this doctor."
        )

    st.divider()
    st.subheader("📋 Appointment History")

    appointments = rows_as_dicts(
        get_patient_appointments(patient_id)
    )

    show_table(appointments)

    active_appointments = [
        a for a in appointments
        if str(a.get("status", "")).lower() == "booked"
    ]

    if active_appointments:
        st.subheader("Cancel Appointment")

        cancel_options = {
            f"Booking #{a['id']} · {a['appointment_time']}": a["id"]
            for a in active_appointments
        }

        selected_cancel = st.selectbox(
            "Select Appointment",
            list(cancel_options.keys()),
        )

        confirm_cancel = st.checkbox(
            "Confirm cancellation"
        )

        if st.button(
            "❌ Cancel Appointment",
            disabled=not confirm_cancel,
        ):
            try:
                result = cancel_appointment(
                    cancel_options[selected_cancel]
                )

                if succeeded(result):
                    show_success_after_rerun(
                        "Appointment cancelled successfully."
                    )
                else:
                    st.error(failure_message(result))

            except Exception as exc:
                st.error(f"Cancellation failed: {exc}")


# ============================================================
# MEDICAL RECORDS
# ============================================================

elif page == "📋 Medical Records":

    st.header("📋 Medical Records")

    if patient_id is None:
        st.warning("Select a patient first.")
        st.stop()

    st.write(f"**Patient:** {patient['name']}")

    records = rows_as_dicts(
        get_medical_history(patient_id)
    )

    show_table(records)

    st.subheader("➕ Add Medical Record")

    with st.form("add_medical_record"):

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
            type="primary",
        )

    if save:
        if not diagnosis.strip():
            st.error("Diagnosis or condition is required.")
        else:
            try:
                add_medical_record(
                    patient_id,
                    diagnosis.strip(),
                    treatment,
                    notes,
                )

                show_success_after_rerun(
                    "Medical record saved successfully."
                )

            except Exception as exc:
                st.error(f"Could not save record: {exc}")

    if records:
        st.subheader("✏️ Update Existing Record")

        choices = {
            f"#{r['id']} · {r['diagnosis']}": r
            for r in records
        }

        selected_record = st.selectbox(
            "Choose Record",
            list(choices.keys()),
        )

        record = choices[selected_record]

        with st.form("edit_medical_record"):

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
                "💾 Save Changes",
                type="primary",
            )

        if update:
            if not new_diagnosis.strip():
                st.error("Diagnosis is required.")
            else:
                try:
                    update_medical_record(
                        record["id"],
                        new_diagnosis,
                        new_treatment,
                        new_notes,
                    )

                    show_success_after_rerun(
                        "Medical record updated successfully."
                    )

                except Exception as exc:
                    st.error(f"Update failed: {exc}")


# ============================================================
# AI HISTORY SUMMARY
# ============================================================

elif page == "🩺 History Summary":

    st.header("🩺 AI Medical History Summary")

    if patient_id is None:
        st.warning("Select a patient first.")
        st.stop()

    records = get_medical_history(patient_id)
    show_table(records)

    if st.button(
        "✨ Generate History Summary",
        type="primary",
        disabled=not bool(records),
    ):
        with st.spinner("Generating history summary..."):
            try:
                context = generate_history_context(patient_id)

                prompt = (
                    "Summarize the supplied patient history "
                    "accurately. Include documented conditions, "
                    "treatments, and relevant notes. Do not "
                    "invent details or prescribe treatment.\n\n"
                    + context
                )

                summary = generate_ai_response(prompt)

                st.session_state["history_summary"] = {
                    "patient_id": patient_id,
                    "text": summary,
                }

                st.toast(
                    "History summary generated!",
                    icon="✅",
                )

            except Exception as exc:
                st.error(f"Summary failed: {exc}")

    saved = st.session_state.get("history_summary")

    if saved and saved["patient_id"] == patient_id:
        st.subheader("Generated Summary")
        st.write(saved["text"])


# ============================================================
# MEDICAL RESEARCH
# ============================================================

elif page == "🔎 Medical Research":

    st.header("🔎 Medical Research")

    topic = st.text_input(
        "Search Medical Topic",
        placeholder="Example: chronic kidney disease",
    )

    if st.button(
        "🔍 Search Medical Sources",
        type="primary",
    ):
        if not topic.strip():
            st.warning("Enter a medical topic.")
        else:
            with st.spinner("Searching medical information..."):
                try:
                    result = retrieve_medical_information(topic)

                    st.session_state["research"] = {
                        "topic": topic,
                        "result": result,
                    }

                    st.toast(
                        "Medical search completed!",
                        icon="✅",
                    )

                except Exception as exc:
                    st.error(f"Search failed: {exc}")

    saved = st.session_state.get("research")

    if saved and saved["topic"] == topic:
        sources = saved["result"].get("sources", [])

        if not sources:
            st.info("No matching sources found.")

        for source in sources:
            with st.container(border=True):
                st.subheader(
                    source.get("title", "Medical Information")
                )

                st.write(source.get("content", ""))

                url = source.get("url", "")

                if (
                    url.startswith("https://medlineplus.gov/")
                    or url.startswith(
                        "https://www.medlineplus.gov/"
                    )
                ):
                    st.link_button(
                        "Read Trusted Source",
                        url,
                    )


# ============================================================
# AI HEALTHCARE ASSISTANT
# ============================================================

elif page == "🤖 AI Assistant":

    st.header("🤖 AI Healthcare Assistant")

    if patient_id is None:
        st.warning("Select a patient first.")
        st.stop()

    query = st.text_area(
        "Describe Your Request",
        value=(
            "Summarize patient medical history, "
            "find a nephrologist, and research "
            "chronic kidney disease."
        ),
        height=140,
    )

    if st.button(
        "✨ Run Healthcare Agent",
        type="primary",
        use_container_width=True,
    ):
        if not query.strip():
            st.warning("Enter a request.")
        else:
            with st.spinner("Executing AI agent..."):
                try:
                    from healthcare.agent import (
                        run_healthcare_agent,
                    )

                    result = run_healthcare_agent(
                        query,
                        patient_id,
                    )

                    st.session_state["agent_output"] = {
                        "patient_id": patient_id,
                        "result": result,
                    }

                    st.toast(
                        "Agent execution completed!",
                        icon="✅",
                    )

                except Exception as exc:
                    st.error(f"Agent failed: {exc}")

    saved = st.session_state.get("agent_output")

    if saved and saved["patient_id"] == patient_id:
        result = saved["result"]

        st.subheader("Agent Response")
        st.write(result.get("response", ""))

        with st.expander("Agent Plan"):
            st.write(result.get("plan", ""))

        with st.expander("Execution Trace"):
            st.write(result.get("execution_trace", []))

        with st.expander("Medical Sources"):
            st.write(result.get("medical_sources", []))

    if st.button("📅 Open Appointment Booking"):
        navigate("📅 Appointments")


# ============================================================
# FAISS MEMORY
# ============================================================

elif page == "🧠 FAISS Memory":

    st.header("🧠 Patient Semantic Memory")

    if patient_id is None:
        st.warning("Select a patient first.")
        st.stop()

    query = st.text_input(
        "Search Patient History",
        placeholder="Example: kidney disease history",
    )

    if st.button(
        "🔍 Search Semantic Memory",
        type="primary",
    ):
        if not query.strip():
            st.warning("Enter a search query.")
        else:
            with st.spinner("Searching vector memory..."):
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

                    for index, item in enumerate(matches, 1):
                        with st.container(border=True):
                            st.subheader(
                                f"Memory Match {index}"
                            )

                            st.write(item.get("content", ""))

                            similarity = float(
                                item.get("similarity", 0)
                            )

                            st.caption(
                                f"Similarity: {similarity:.3f}"
                            )

                except Exception as exc:
                    st.error(f"Memory search failed: {exc}")


# ============================================================
# MONITORING
# ============================================================

elif page == "📊 Monitoring":

    st.header("📊 Evaluation and Monitoring")

    try:
        from healthcare.monitoring import (
            get_agent_logs,
            get_monitoring_metrics,
        )

        st.subheader("Agent Monitoring Metrics")
        st.json(get_monitoring_metrics())

        st.subheader("Execution Logs")
        show_table(get_agent_logs(limit=100))

    except Exception as exc:
        st.warning(f"Monitoring unavailable: {exc}")

    try:
        from healthcare.evaluation import (
            get_evaluation_metrics,
        )

        st.subheader("Evaluation Metrics")
        st.json(get_evaluation_metrics())

    except Exception as exc:
        st.warning(f"Evaluation unavailable: {exc}")


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "MediFlow AI | Intelligent Healthcare Management | "
    "Gemini AI • LangGraph • FAISS • Streamlit"
)
