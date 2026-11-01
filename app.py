
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

from healthcare.ui_style import (
    apply_custom_style,
    render_hero,
    render_feature_cards,
)
from healthcare.database import (
    initialize_database,
    get_connection,
)
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
from healthcare.medical_search import (
    retrieve_medical_information,
)
from healthcare.config import generate_ai_response


# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="MediFlow AI | Healthcare Workspace",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_style()
initialize_database()


# ==========================================================
# DATABASE EXTENSIONS
# ==========================================================

def create_patient(name, age):
    name = name.strip()

    if len(name) < 2:
        raise ValueError(
            "Patient name must contain at least 2 characters."
        )

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO patients (name, age)
            VALUES (?, ?)
            """,
            (name, int(age)),
        )
        conn.commit()
        return cursor.lastrowid


def seed_additional_doctors():
    """
    Adds fictional doctors across multiple departments.
    Existing doctors are preserved.
    """

    demo_doctors = [
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
            ).fetchall()
        }

        for name, specialization in demo_doctors:
            if (name, specialization) not in existing:
                conn.execute(
                    """
                    INSERT INTO doctors (name, specialization)
                    VALUES (?, ?)
                    """,
                    (name, specialization),
                )

        conn.commit()


try:
    seed_additional_doctors()
except Exception as exc:
    st.warning(
        f"Could not initialize additional demo doctors: {exc}"
    )


# ==========================================================
# NAVIGATION AND NOTIFICATIONS
# ==========================================================

PAGES = [
    "🏠 Dashboard",
    "👤 Patients",
    "📅 Appointments",
    "📋 Medical Records",
    "🩺 History Summary",
    "🔎 Medical Research",
    "🤖 AI Healthcare Assistant",
    "🧠 FAISS Memory",
    "📊 Evaluation & Monitoring",
]

if "_next_page" in st.session_state:
    st.session_state["page"] = st.session_state.pop(
        "_next_page"
    )


def navigate(page_name):
    st.session_state["_next_page"] = page_name
    st.rerun()


def notify_success(message):
    st.session_state["_success_notification"] = message
    st.rerun()


def show_table(data, empty_message="No records found."):
    if data:
        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(empty_message)


def normalize_rows(rows):
    return [dict(row) for row in rows]


def operation_succeeded(result):
    if isinstance(result, dict):
        return result.get("success", True)
    return result is not False


def operation_message(result, fallback):
    if isinstance(result, dict):
        return result.get("message", fallback)
    return fallback


# ==========================================================
# DEPARTMENT GUIDANCE
# ==========================================================

DEPARTMENT_GUIDE = {
    "Kidney or urinary system concerns": "Nephrology",
    "Heart-related concerns": "Cardiology",
    "Headache, nerves or neurological concerns": "Neurology",
    "Bone, joint or muscle concerns": "Orthopedics",
    "Skin or hair concerns": "Dermatology",
    "Digestive or stomach concerns": "Gastroenterology",
    "Diabetes or thyroid concerns": "Endocrinology",
    "Breathing or lung concerns": "Pulmonology",
    "Ear, nose or throat concerns": "ENT",
    "Eye or vision concerns": "Ophthalmology",
    "Women's reproductive health": "Gynecology",
    "Mental health concerns": "Psychiatry",
    "Children's health": "Pediatrics",
    "General consultation or unsure": "General Medicine",
}


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    st.title("🏥 MediFlow AI")
    st.caption("INTELLIGENT HEALTHCARE WORKSPACE")

    page = st.radio(
        "Explore modules",
        PAGES,
        key="page",
    )

    st.divider()
    st.subheader("👤 Patient Workspace")

    patients = normalize_rows(get_patients())

    if not patients:
        st.warning("No patients found. Register a demo patient.")
        patient_id = None
        patient = None
    else:
        patient_options = {
            f"{p['name']} • ID {p['id']}": p["id"]
            for p in patients
        }

        patient_labels = list(patient_options.keys())

        selected_patient = st.selectbox(
            "Select Patient",
            patient_labels,
            key="selected_patient",
        )

        patient_id = patient_options[selected_patient]
        patient = get_patient(patient_id)

        if patient:
            st.markdown(f"**Name:** {patient['name']}")
            st.markdown(f"**Age:** {patient['age']} years")
            st.markdown(f"**Patient ID:** {patient_id}")

    if st.button(
        "➕ Register New Patient",
        use_container_width=True,
        key="sidebar_register_patient",
    ):
        navigate("👤 Patients")

    st.divider()

    st.caption("✨ Powered by Google Gemini")
    st.caption("Educational clinical-style prototype")


# ==========================================================
# NOTIFICATION DISPLAY
# ==========================================================

if "_success_notification" in st.session_state:
    success_message = st.session_state.pop(
        "_success_notification"
    )

    st.toast(success_message, icon="✅")
    st.success(success_message)


# ==========================================================
# MAIN HEADER
# ==========================================================

st.title("🏥 MediFlow AI")

st.caption(
    "Intelligent Healthcare Workspace • "
    "Gemini AI • LangGraph • FAISS • Streamlit"
)

st.info(
    "Educational demonstration using fictional patients "
    "and simulated appointments. Not for real clinical care."
)


# ==========================================================
# DASHBOARD
# ==========================================================

if page == "🏠 Dashboard":

    render_hero()

    all_doctors = normalize_rows(get_doctors())

    patient_history = (
        normalize_rows(get_medical_history(patient_id))
        if patient_id is not None
        else []
    )

    appointments = (
        normalize_rows(get_patient_appointments(patient_id))
        if patient_id is not None
        else []
    )

    active_appointments = [
        item for item in appointments
        if item.get("status") == "Booked"
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Patients", len(patients))
    col2.metric("👨‍⚕️ Doctors", len(all_doctors))
    col3.metric("📋 Medical Records", len(patient_history))
    col4.metric(
        "📅 Active Appointments",
        len(active_appointments),
    )

    st.markdown("## ✨ Explore the Platform")

    render_feature_cards()

    st.markdown("## 🚀 Quick Actions")

    quick1, quick2, quick3 = st.columns(3)

    with quick1:
        if st.button(
            "➕ Register Patient",
            key="dashboard_register",
            use_container_width=True,
        ):
            navigate("👤 Patients")

    with quick2:
        if st.button(
            "📅 Book Appointment",
            key="dashboard_book",
            use_container_width=True,
        ):
            navigate("📅 Appointments")

    with quick3:
        if st.button(
            "📋 Add Medical Record",
            key="dashboard_record",
            use_container_width=True,
        ):
            navigate("📋 Medical Records")

    st.markdown("## 👤 Selected Patient")

    if patient:
        with st.container(border=True):
            st.write(f"**Name:** {patient['name']}")
            st.write(f"**Age:** {patient['age']}")
            st.write(f"**Patient ID:** {patient_id}")

    st.markdown("## 📋 Recent Medical History")

    show_table(
        patient_history[:5],
        "No medical records available yet.",
    )

    st.markdown("## 📅 Upcoming Simulated Appointments")

    show_table(
        active_appointments,
        "No active appointments.",
    )


# ==========================================================
# PATIENT REGISTRATION
# ==========================================================

elif page == "👤 Patients":

    st.header("👤 Patient Registration")

    st.write(
        "Register a new fictional patient. "
        "A success notification will appear after saving."
    )

    with st.form(
        "register_patient_form",
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
            step=1,
        )

        submitted = st.form_submit_button(
            "✅ Register Patient",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if len(name.strip()) < 2:
            st.error(
                "Please enter a valid patient name."
            )
        else:
            try:
                new_patient_id = create_patient(
                    name,
                    age,
                )

                notify_success(
                    f"Patient {name.strip()} registered "
                    f"successfully! Patient ID: {new_patient_id}"
                )

            except Exception as exc:
                st.error(
                    f"Patient registration failed: {exc}"
                )

    st.divider()

    st.subheader("👥 Registered Patients")

    show_table(
        normalize_rows(get_patients()),
        "No registered patients.",
    )


# ==========================================================
# SMART APPOINTMENTS
# ==========================================================

elif page == "📅 Appointments":

    st.header("📅 Smart Appointment Booking")

    if patient_id is None:
        st.warning("Register a patient first.")
        st.stop()

    st.success(
        f"Selected Patient: {patient['name']}"
    )

    st.markdown("### Step 1 — Select Patient Concern")

    concern = st.selectbox(
        "What type of consultation is required?",
        list(DEPARTMENT_GUIDE.keys()),
        key="booking_concern",
    )

    suggested_department = DEPARTMENT_GUIDE[concern]

    st.info(
        f"Suggested department: **{suggested_department}**"
    )

    st.caption(
        "This is a general department suggestion, "
        "not a diagnosis or medical triage decision."
    )

    st.markdown("### Step 2 — Choose Department")

    all_doctors = normalize_rows(get_doctors())

    departments = sorted({
        doctor["specialization"]
        for doctor in all_doctors
    })

    if not departments:
        st.error("No doctors available.")
        st.stop()

    department = st.selectbox(
        "Medical Department",
        departments,
        index=(
            departments.index(suggested_department)
            if suggested_department in departments
            else 0
        ),
        key=f"department_{concern}",
    )

    st.markdown("### Step 3 — Choose Doctor")

    department_doctors = [
        doctor for doctor in all_doctors
        if doctor["specialization"] == department
    ]

    if not department_doctors:
        st.warning(
            "No doctors currently listed for this department."
        )
    else:
        doctor_options = {
            (
                f"{doctor['name']} "
                f"— {doctor['specialization']}"
            ): doctor["id"]
            for doctor in department_doctors
        }

        doctor_label = st.selectbox(
            "Doctor Name",
            list(doctor_options.keys()),
            key="doctor_dropdown",
        )

        doctor_id = doctor_options[doctor_label]

        st.markdown("### Step 4 — Available Time Slots")

        try:
            slots = get_available_slots(
                doctor_id,
                days=7,
            )
        except Exception as exc:
            slots = []
            st.error(
                f"Could not retrieve available slots: {exc}"
            )

        if slots:
            selected_slot = st.selectbox(
                "Appointment Date and Time",
                slots,
                key="appointment_slot",
            )

            st.markdown("### Step 5 — Booking Confirmation")

            with st.container(border=True):
                st.write(
                    f"**Patient:** {patient['name']}"
                )
                st.write(
                    f"**Department:** {department}"
                )
                st.write(
                    f"**Doctor:** {doctor_label}"
                )
                st.write(
                    f"**Appointment:** {selected_slot}"
                )

                confirm_booking = st.checkbox(
                    "I confirm this simulated appointment.",
                    key="confirm_booking",
                )

                if st.button(
                    "✅ Confirm Appointment",
                    type="primary",
                    disabled=not confirm_booking,
                    use_container_width=True,
                    key="confirm_appointment_button",
                ):

                    try:
                        result = book_appointment(
                            patient_id,
                            doctor_id,
                            selected_slot,
                        )

                        if operation_succeeded(result):
                            notify_success(
                                "Appointment booked successfully! "
                                f"Doctor: {doctor_label}. "
                                f"Time: {selected_slot}"
                            )
                        else:
                            st.error(
                                operation_message(
                                    result,
                                    "Booking failed.",
                                )
                            )

                    except Exception as exc:
                        st.error(
                            f"Appointment booking failed: {exc}"
                        )

        else:
            st.warning(
                "No appointment slots are available "
                "for this doctor in the next seven days."
            )

    st.divider()

    st.subheader("📋 Appointment History")

    bookings = normalize_rows(
        get_patient_appointments(patient_id)
    )

    show_table(
        bookings,
        "No appointments found.",
    )

    active_bookings = [
        item for item in bookings
        if item.get("status") == "Booked"
    ]

    if active_bookings:
        st.subheader("❌ Cancel Appointment")

        booking_options = {
            (
                f"Booking #{item['id']} — "
                f"{item.get('doctor_name', 'Doctor')} — "
                f"{item['appointment_time']}"
            ): item["id"]
            for item in active_bookings
        }

        booking_label = st.selectbox(
            "Select Booking",
            list(booking_options.keys()),
            key="cancel_booking_dropdown",
        )

        confirm_cancel = st.checkbox(
            "Confirm cancellation",
            key="confirm_cancellation",
        )

        if st.button(
            "Cancel Selected Appointment",
            disabled=not confirm_cancel,
            key="cancel_booking_button",
        ):
            try:
                result = cancel_appointment(
                    booking_options[booking_label]
                )

                if operation_succeeded(result):
                    notify_success(
                        "Appointment cancelled successfully."
                    )
                else:
                    st.error(
                        operation_message(
                            result,
                            "Cancellation failed.",
                        )
                    )

            except Exception as exc:
                st.error(
                    f"Cancellation failed: {exc}"
                )


# ==========================================================
# MEDICAL RECORDS
# ==========================================================

elif page == "📋 Medical Records":

    st.header("📋 Electronic Medical Records")

    if patient_id is None:
        st.warning("Register a patient first.")
        st.stop()

    st.write(
        f"**Selected Patient:** {patient['name']}"
    )

    records = normalize_rows(
        get_medical_history(patient_id)
    )

    st.subheader("Existing Medical Records")

    show_table(
        records,
        "No medical history recorded.",
    )

    st.subheader("➕ Add Medical Record")

    with st.form(
        "add_record_form",
        clear_on_submit=True,
    ):
        diagnosis = st.text_input(
            "Diagnosis or Condition",
        )

        treatment = st.text_area(
            "Treatment Details",
        )

        notes = st.text_area(
            "Additional Notes",
        )

        add_submitted = st.form_submit_button(
            "💾 Save Medical Record",
            type="primary",
        )

    if add_submitted:
        if not diagnosis.strip():
            st.error(
                "Diagnosis or condition is required."
            )
        else:
            try:
                add_medical_record(
                    patient_id,
                    diagnosis.strip(),
                    treatment,
                    notes,
                )

                notify_success(
                    "Medical record saved successfully."
                )

            except Exception as exc:
                st.error(
                    f"Could not save record: {exc}"
                )

    if records:
        st.divider()
        st.subheader("✏️ Update Existing Record")

        record_options = {
            f"#{item['id']} — {item['diagnosis']}": item
            for item in records
        }

        record_label = st.selectbox(
            "Select Medical Record",
            list(record_options.keys()),
            key="record_to_edit",
        )

        selected_record = record_options[record_label]

        with st.form("edit_medical_record_form"):

            updated_diagnosis = st.text_input(
                "Update Diagnosis",
                value=selected_record.get(
                    "diagnosis", ""
                ) or "",
            )

            updated_treatment = st.text_area(
                "Update Treatment",
                value=selected_record.get(
                    "treatment", ""
                ) or "",
            )

            updated_notes = st.text_area(
                "Update Notes",
                value=selected_record.get(
                    "notes", ""
                ) or "",
            )

            update_submitted = st.form_submit_button(
                "💾 Update Record",
                type="primary",
            )

        if update_submitted:
            if not updated_diagnosis.strip():
                st.error("Diagnosis cannot be empty.")
            else:
                try:
                    update_medical_record(
                        selected_record["id"],
                        updated_diagnosis,
                        updated_treatment,
                        updated_notes,
                    )

                    notify_success(
                        "Medical record updated successfully."
                    )

                except Exception as exc:
                    st.error(
                        f"Could not update record: {exc}"
                    )


# ==========================================================
# AI MEDICAL HISTORY SUMMARY
# ==========================================================

elif page == "🩺 History Summary":

    st.header("🩺 AI Medical History Summary")

    if patient_id is None:
        st.warning("Select a patient first.")
        st.stop()

    st.write(
        f"**Patient:** {patient['name']}"
    )

    records = normalize_rows(
        get_medical_history(patient_id)
    )

    show_table(
        records,
        "No medical records available.",
    )

    if st.button(
        "✨ Generate History Summary",
        type="primary",
        disabled=not bool(records),
        key="generate_history_summary",
    ):
        with st.spinner(
            "Generating a medical history summary..."
        ):
            try:
                history = generate_history_context(
                    patient_id
                )

                prompt = (
                    "You are summarizing fictional "
                    "patient records for an educational "
                    "software demonstration.\n"
                    "Summarize only the supplied records.\n"
                    "Include documented diagnoses, "
                    "treatments and notes.\n"
                    "Do not invent missing details.\n"
                    "Do not prescribe medication or "
                    "make a new diagnosis.\n\n"
                    f"PATIENT HISTORY:\n{history}"
                )

                summary = generate_ai_response(
                    prompt
                )

                st.session_state["history_summary"] = {
                    "patient_id": patient_id,
                    "content": summary,
                }

                st.toast(
                    "History summary generated!",
                    icon="✅",
                )

            except Exception as exc:
                st.error(
                    f"AI summary failed: {exc}"
                )

    saved_summary = st.session_state.get(
        "history_summary"
    )

    if (
        saved_summary
        and saved_summary["patient_id"] == patient_id
    ):
        st.subheader("Generated Summary")

        st.write(
            saved_summary["content"]
        )

        st.caption(
            "AI-generated content must be checked "
            "against the source records."
        )


# ==========================================================
# MEDICAL RESEARCH
# ==========================================================

elif page == "🔎 Medical Research":

    st.header("🔎 Trusted Medical Research")

    st.write(
        "Search for educational medical information "
        "from trusted external sources."
    )

    topic = st.text_input(
        "Medical Topic or Disease",
        value="chronic kidney disease",
        key="medical_research_topic",
    )

    if st.button(
        "🔍 Search Medical Sources",
        type="primary",
        key="medical_search_button",
    ):

        if not topic.strip():
            st.warning("Enter a search topic.")

        else:
            with st.spinner(
                "Searching trusted medical information..."
            ):
                try:
                    result = retrieve_medical_information(
                        topic
                    )

                    st.session_state["medical_search_result"] = {
                        "topic": topic,
                        "result": result,
                    }

                except Exception as exc:
                    st.error(
                        f"Medical search failed: {exc}"
                    )

    saved_research = st.session_state.get(
        "medical_search_result"
    )

    if (
        saved_research
        and saved_research["topic"] == topic
    ):
        sources = saved_research["result"].get(
            "sources", []
        )

        if sources:
            st.success(
                f"Found {len(sources)} medical sources."
            )

            for source in sources:
                with st.container(border=True):
                    st.subheader(
                        source.get(
                            "title",
                            "Medical Source",
                        )
                    )

                    st.write(
                        source.get(
                            "content",
                            "No summary available.",
                        )
                    )

                    url = source.get("url", "")

                    if url.startswith(
                        "https://medlineplus.gov/"
                    ) or url.startswith(
                        "https://www.medlineplus.gov/"
                    ):
                        st.link_button(
                            "Open Trusted Source",
                            url,
                        )
        else:
            st.warning(
                "No verified results were returned. "
                "Try a broader medical topic."
            )


# ==========================================================
# AGENTIC AI ASSISTANT
# ==========================================================

elif page == "🤖 AI Healthcare Assistant":

    st.header("🤖 Agentic Healthcare Assistant")

    if patient_id is None:
        st.warning("Select a patient first.")
        st.stop()

    st.write(
        f"**Selected Patient:** {patient['name']}"
    )

    examples = {
        "Kidney Care": (
            "Summarize this patient's medical history, "
            "find available nephrologist appointments, "
            "and research chronic kidney disease."
        ),
        "Heart Care": (
            "Review patient history, find cardiology "
            "appointments, and retrieve heart health "
            "information."
        ),
        "General Care": (
            "Summarize the patient's medical records "
            "and find available general medicine doctors."
        ),
        "Custom Request": "",
    }

    example = st.selectbox(
        "Try an Example",
        list(examples.keys()),
        key="agent_example",
    )

    query = st.text_area(
        "Enter Healthcare Request",
        value=examples[example],
        height=150,
        key=f"agent_query_{example}",
    )

    if st.button(
        "✨ Run AI Healthcare Agent",
        type="primary",
        use_container_width=True,
        key="run_agent_button",
    ):

        if not query.strip():
            st.warning(
                "Enter a healthcare request."
            )

        else:
            with st.spinner(
                "Gemini and LangGraph are processing..."
            ):
                try:
                    from healthcare.agent import (
                        run_healthcare_agent,
                    )

                    result = run_healthcare_agent(
                        query,
                        patient_id,
                    )

                    st.session_state["agent_result"] = {
                        "patient_id": patient_id,
                        "result": result,
                    }

                    st.toast(
                        "Agent execution completed!",
                        icon="✅",
                    )

                except Exception as exc:
                    st.error(
                        f"AI agent execution failed: {exc}"
                    )

    saved_agent = st.session_state.get(
        "agent_result"
    )

    if (
        saved_agent
        and saved_agent["patient_id"] == patient_id
    ):
        result = saved_agent["result"]

        st.subheader("🤖 Agent Response")

        st.write(
            result.get(
                "response",
                "No response returned.",
            )
        )

        with st.expander("🧩 Planning Breakdown"):
            st.write(
                result.get(
                    "plan",
                    "No plan available.",
                )
            )

        with st.expander("🔍 Execution Trace"):
            st.write(
                result.get(
                    "execution_trace",
                    [],
                )
            )

        with st.expander("📚 Retrieved Sources"):
            st.write(
                result.get(
                    "medical_sources",
                    [],
                )
            )

    if st.button(
        "📅 Continue to Appointment Booking",
        key="agent_to_appointments",
    ):
        navigate("📅 Appointments")


# ==========================================================
# FAISS VECTOR MEMORY
# ==========================================================

elif page == "🧠 FAISS Memory":

    st.header("🧠 AI Semantic Patient Memory")

    if patient_id is None:
        st.warning("Select a patient first.")
        st.stop()

    st.write(
        f"**Patient:** {patient['name']}"
    )

    memory_query = st.text_input(
        "Search Patient History",
        placeholder="Example: kidney disease history",
        key="memory_search_query",
    )

    if st.button(
        "🔍 Search Vector Memory",
        type="primary",
        key="search_vector_memory",
    ):

        if not memory_query.strip():
            st.warning("Enter a search query.")

        else:
            with st.spinner(
                "Searching FAISS semantic memory..."
            ):
                try:
                    from healthcare.memory import (
                        retrieve_patient_memory,
                    )

                    matches = retrieve_patient_memory(
                        patient_id,
                        memory_query,
                    )

                    if matches:
                        st.success(
                            f"Found {len(matches)} memory matches."
                        )

                        for index, item in enumerate(
                            matches,
                            1,
                        ):
                            with st.container(border=True):
                                st.subheader(
                                    f"Memory Match {index}"
                                )

                                st.write(
                                    item.get(
                                        "content",
                                        "",
                                    )
                                )

                                similarity = float(
                                    item.get(
                                        "similarity",
                                        0,
                                    )
                                )

                                st.caption(
                                    f"Similarity score: "
                                    f"{similarity:.3f}"
                                )
                    else:
                        st.info(
                            "No matching patient memory found."
                        )

                except Exception as exc:
                    st.error(
                        f"FAISS memory failed: {exc}"
                    )


# ==========================================================
# EVALUATION AND MONITORING
# ==========================================================

elif page == "📊 Evaluation & Monitoring":

    st.header("📊 Evaluation and Monitoring")

    st.write(
        "Review agent execution records "
        "and available evaluation metrics."
    )

    try:
        from healthcare.monitoring import (
            get_agent_logs,
            get_monitoring_metrics,
        )

        metrics = get_monitoring_metrics()

        st.subheader("Execution Metrics")
        st.json(metrics)

        logs = get_agent_logs(limit=100)

        st.subheader("Agent Execution Logs")
        show_table(
            logs,
            "No execution logs available.",
        )

    except Exception as exc:
        st.warning(
            f"Monitoring could not load: {exc}"
        )

    try:
        from healthcare.evaluation import (
            get_evaluation_metrics,
        )

        evaluation = get_evaluation_metrics()

        st.subheader("Model Evaluation")
        st.json(evaluation)

    except Exception as exc:
        st.warning(
            f"Evaluation could not load: {exc}"
        )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

st.caption(
    "🏥 MediFlow AI | Gemini AI • LangGraph • "
    "FAISS • Streamlit | Educational Prototype"
)
