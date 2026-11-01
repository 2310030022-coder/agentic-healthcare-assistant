
import streamlit as st
import pandas as pd

from healthcare.ui_style import (
    apply_custom_style,
    render_hero,
    render_feature_cards
)

from healthcare.database import initialize_database
from healthcare.records import (
    get_patients,
    get_patient,
    get_medical_history,
    add_medical_record,
    update_medical_record
)
from healthcare.appointments import (
    get_doctors,
    get_available_slots,
    book_appointment,
    get_patient_appointments,
    cancel_appointment
)
from healthcare.agent import run_healthcare_agent
from healthcare.memory import retrieve_patient_memory
from healthcare.medical_search import retrieve_medical_information
from healthcare.monitoring import (
    monitor_execution,
    get_agent_logs,
    get_monitoring_metrics
)
from healthcare.evaluation import (
    evaluate_response,
    get_evaluation_metrics
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="MediFlow AI | Healthcare Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_style()
initialize_database()


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def section_header(icon, title, description):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(110deg,#eaf3ff,#f1edff);
            border: 1px solid #dce7fb;
            border-radius: 18px;
            padding: 20px 24px;
            margin: 12px 0 24px;
        ">
            <h2 style="margin:0;color:#244b9b;">
                {icon} {title}
            </h2>
            <p style="
                color:#60728f;
                margin:8px 0 0;
                font-size:15px;
            ">{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def safe_monitor(module, action, function, *args, **kwargs):
    try:
        return monitor_execution(
            module, action, function, *args, **kwargs
        )
    except Exception as exc:
        st.error(f"{action} failed: {exc}")
        return None


def show_dataframe(rows, empty_message="No data available."):
    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(empty_message)


def display_result(result):
    if isinstance(result, dict):
        if result.get("success"):
            st.success(result.get("message", "Action completed."))
        else:
            st.error(result.get("message", "Action failed."))
    else:
        st.success("Operation completed.")


# --------------------------------------------------
# TOP HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="main-title">
        🏥 MediFlow AI
    </div>
    <div class="subtitle">
        Intelligent Healthcare Task Automation Platform
        • Gemini AI • LangGraph • FAISS RAG
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "🎓 Educational capstone using fictional patients and "
    "simulated appointments. Not for real medical care, "
    "diagnosis, or clinical decisions."
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🏥 MediFlow AI")
    st.caption("INTELLIGENT HEALTHCARE WORKSPACE")
    st.divider()

    page = st.radio(
        "Explore modules",
        [
            "🏠 Dashboard",
            "🤖 AI Healthcare Assistant",
            "📅 Appointments",
            "📋 Medical Records",
            "🧠 FAISS Memory",
            "🔎 Medical Research",
            "👨‍⚕️ Doctor View",
            "📊 Evaluation & Monitoring"
        ]
    )

    st.divider()
    st.markdown("### 👤 Demo Patient")

    patients = get_patients()

    patient_options = {
        f"{p['name']} • ID {p['id']}": p["id"]
        for p in patients
    }

    selected_patient = st.selectbox(
        "Select patient",
        list(patient_options.keys())
    )

    patient_id = patient_options[selected_patient]

    patient = get_patient(patient_id)

    if patient:
        st.markdown(f"**Name:** {patient['name']}")
        st.markdown(f"**Age:** {patient['age']} years")

    st.caption(
        "Demo selection is not authentication. "
        "Use fictional patient information only."
    )

    st.divider()
    st.caption("✨ Powered by Google Gemini")


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

if page == "🏠 Dashboard":
    render_hero()

    section_header(
        "📊",
        "Healthcare Overview",
        "A real-time overview of the fictional patient "
        "records and simulated appointment system."
    )

    appointments = get_patient_appointments(patient_id)
    history = get_medical_history(patient_id)

    active = sum(
        1 for appointment in appointments
        if appointment.get("status") == "Booked"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Patients", len(patients))
    c2.metric("👨‍⚕️ Doctors", len(get_doctors()))
    c3.metric("📋 Medical Records", len(history))
    c4.metric("📅 Active Bookings", active)

    st.markdown("### ✨ Explore the Platform")
    render_feature_cards()

    left, right = st.columns([1, 1.5])

    with left:
        st.markdown("### 👤 Patient Profile")

        with st.container(border=True):
            st.markdown(f"#### {patient['name']}")
            st.write(f"**Patient ID:** {patient['id']}")
            st.write(f"**Age:** {patient['age']} years")
            st.write("**Account:** Fictional demo patient")

    with right:
        st.markdown("### 📋 Recent Medical History")
        show_dataframe(
            history[:5],
            "No medical history has been recorded."
        )

    st.markdown("### 📅 Upcoming Appointments")

    booked = [
        appointment for appointment in appointments
        if appointment.get("status") == "Booked"
    ]

    show_dataframe(booked, "No active appointments.")


# --------------------------------------------------
# AI HEALTHCARE ASSISTANT
# --------------------------------------------------

elif page == "🤖 AI Healthcare Assistant":
    section_header(
        "🤖",
        "Gemini Healthcare Agent",
        "Describe a multi-step task and explore how "
        "the agent plans and coordinates healthcare tools."
    )

    st.markdown("### 💬 Ask MediFlow AI")

    examples = {
        "Kidney Care": (
            "Summarize this patient's medical history, "
            "find available nephrologist appointments, "
            "and research chronic kidney disease."
        ),
        "Heart Care": (
            "Find available cardiology appointments "
            "and search for trusted information "
            "about heart disease."
        ),
        "Patient History": (
            "Summarize the selected patient's "
            "medical history."
        )
    }

    selected_example = st.selectbox(
        "Try an example",
        list(examples.keys())
    )

    query = st.text_area(
        "Enter your healthcare request",
        value=examples[selected_example],
        height=150
    )

    if st.button(
        "✨ Run AI Healthcare Agent",
        type="primary",
        use_container_width=True
    ):
        if not query.strip():
            st.warning("Please enter a healthcare request.")
        else:
            with st.spinner(
                "Gemini is planning and executing your request..."
            ):
                result = safe_monitor(
                    "LangGraph",
                    "run_healthcare_agent",
                    run_healthcare_agent,
                    query,
                    patient_id
                )

                if result is not None:
                    st.session_state["agent_result"] = result
                    st.session_state["agent_query"] = query
                    st.session_state["agent_patient_id"] = patient_id

    result = st.session_state.get("agent_result")

    if (
        result is not None
        and st.session_state.get("agent_patient_id") == patient_id
    ):
        st.markdown("### ✨ AI Response")

        with st.container(border=True):
            st.markdown(result.get("response", ""))

        tab1, tab2, tab3 = st.tabs([
            "🧩 Agent Plan",
            "🔍 Execution Trace",
            "📚 Trusted Sources"
        ])

        with tab1:
            st.markdown(
                result.get("plan", "No plan available.")
            )

        with tab2:
            trace = result.get("execution_trace", [])

            if trace:
                for index, step in enumerate(trace, start=1):
                    st.write(f"**Step {index}:** {step}")
            else:
                st.info("No execution trace available.")

        with tab3:
            sources = result.get("medical_sources", [])

            if sources:
                for source in sources:
                    st.markdown(
                        f"**[{source['title']}]({source['url']})**"
                    )
                    st.caption(source.get("source", "MedlinePlus"))
            else:
                st.info("No medical sources retrieved.")

        st.markdown("### 📊 Evaluate Agent Response")

        if st.button("Evaluate Response"):
            evaluation = safe_monitor(
                "Evaluation",
                "evaluate_response",
                evaluate_response,
                st.session_state.get("agent_query", ""),
                result.get("response", "")
            )

            if evaluation is not None:
                st.json(evaluation)
                st.caption(
                    "These are lexical similarity scores, "
                    "not clinical accuracy measurements."
                )


# --------------------------------------------------
# APPOINTMENT MANAGEMENT
# --------------------------------------------------

elif page == "📅 Appointments":
    section_header(
        "📅",
        "Smart Appointment Management",
        "Browse available doctor slots and manage "
        "fictional patient appointments."
    )

    st.markdown("### 👨‍⚕️ Find Your Doctor")

    doctors = get_doctors()

    doctor_options = {
        f"{d['name']} — {d['specialization']}": d["id"]
        for d in doctors
    }

    doctor_label = st.selectbox(
        "Choose a specialist",
        list(doctor_options.keys())
    )

    doctor_id = doctor_options[doctor_label]

    st.markdown("### 🕒 Available Appointment Slots")

    slots = get_available_slots(doctor_id, days=7)

    if slots:
        selected_slot = st.selectbox(
            "Select date and time",
            slots
        )

        st.info(
            f"Selected doctor: {doctor_label}\n\n"
            f"Selected slot: {selected_slot}"
        )

        confirm_booking = st.checkbox(
            "I confirm this simulated appointment booking."
        )

        if st.button(
            "📅 Confirm Appointment",
            type="primary",
            disabled=not confirm_booking
        ):
            result = safe_monitor(
                "Appointments",
                "book_appointment",
                book_appointment,
                patient_id,
                doctor_id,
                selected_slot
            )

            if result is not None:
                display_result(result)

                if result.get("success"):
                    st.rerun()
    else:
        st.warning("No appointment slots available.")

    st.divider()
    st.markdown("### 📋 My Appointments")

    appointments = get_patient_appointments(patient_id)

    show_dataframe(
        appointments,
        "No appointments found for this patient."
    )

    active = [
        appointment for appointment in appointments
        if appointment.get("status") == "Booked"
    ]

    if active:
        st.markdown("### ❌ Cancel Appointment")

        options = {
            (
                f"#{a['id']} — {a['doctor_name']} "
                f"— {a['appointment_time']}"
            ): a["id"]
            for a in active
        }

        selected_appointment = st.selectbox(
            "Select appointment",
            list(options.keys())
        )

        if st.button("Cancel Selected Appointment"):
            selected_id = options[selected_appointment]

            # Only appointment IDs listed for the selected
            # demo patient are offered in this interface.
            result = safe_monitor(
                "Appointments",
                "cancel_appointment",
                cancel_appointment,
                selected_id
            )

            if result is not None:
                display_result(result)

                if result.get("success"):
                    st.rerun()


# --------------------------------------------------
# MEDICAL RECORDS
# --------------------------------------------------

elif page == "📋 Medical Records":
    section_header(
        "📋",
        "Electronic Medical Records",
        "View, create, and update fictional patient "
        "medical history for demonstration."
    )

    st.markdown("### 🩺 Patient History")

    history = get_medical_history(patient_id)

    show_dataframe(
        history,
        "No medical records found."
    )

    st.markdown("### ➕ Add Medical Record")

    with st.form("new_medical_record"):
        diagnosis = st.text_input(
            "Diagnosis",
            placeholder="Example: Chronic Kidney Disease"
        )

        treatment = st.text_area(
            "Treatment",
            placeholder="Enter fictional treatment details"
        )

        notes = st.text_area(
            "Clinical Notes",
            placeholder="Enter fictional clinical observations"
        )

        submitted = st.form_submit_button(
            "💾 Save Medical Record",
            type="primary"
        )

    if submitted:
        if not diagnosis.strip():
            st.warning("Diagnosis is required.")
        else:
            result = safe_monitor(
                "MedicalRecords",
                "add_medical_record",
                add_medical_record,
                patient_id,
                diagnosis,
                treatment,
                notes
            )

            if result is not None:
                display_result(result)

                if result.get("success"):
                    st.rerun()

    if history:
        st.divider()
        st.markdown("### ✏️ Edit Medical Record")

        record_ids = [record["id"] for record in history]

        selected_id = st.selectbox(
            "Select record ID",
            record_ids
        )

        record = next(
            item for item in history
            if item["id"] == selected_id
        )

        with st.form("edit_medical_record"):
            new_diagnosis = st.text_input(
                "Diagnosis",
                value=record.get("diagnosis") or ""
            )

            new_treatment = st.text_area(
                "Treatment",
                value=record.get("treatment") or ""
            )

            new_notes = st.text_area(
                "Notes",
                value=record.get("notes") or ""
            )

            update_submitted = st.form_submit_button(
                "Update Medical Record"
            )

        if update_submitted:
            if not new_diagnosis.strip():
                st.warning("Diagnosis is required.")
            else:
                result = safe_monitor(
                    "MedicalRecords",
                    "update_medical_record",
                    update_medical_record,
                    selected_id,
                    new_diagnosis,
                    new_treatment,
                    new_notes
                )

                if result is not None:
                    display_result(result)

                    if result.get("success"):
                        st.rerun()


# --------------------------------------------------
# FAISS SEMANTIC MEMORY
# --------------------------------------------------

elif page == "🧠 FAISS Memory":
    section_header(
        "🧠",
        "AI Semantic Patient Memory",
        "Search fictional patient records using "
        "sentence embeddings and FAISS similarity."
    )

    memory_query = st.text_input(
        "What would you like to find?",
        placeholder="Example: kidney disease treatment history"
    )

    if st.button(
        "🔍 Search Vector Memory",
        type="primary"
    ):
        if not memory_query.strip():
            st.warning("Please enter a search query.")
        else:
            with st.spinner("Searching semantic memory..."):
                results = safe_monitor(
                    "FAISS",
                    "retrieve_patient_memory",
                    retrieve_patient_memory,
                    patient_id,
                    memory_query
                )

            if results is not None:
                if results:
                    for index, item in enumerate(results, start=1):
                        with st.container(border=True):
                            st.markdown(
                                f"#### 🧠 Memory Match {index}"
                            )

                            st.write(
                                f"**Similarity:** "
                                f"{item.get('similarity', 0):.3f}"
                            )

                            st.text(
                                item.get("content", "")
                            )
                else:
                    st.info("No matching memory found.")


# --------------------------------------------------
# TRUSTED MEDICAL RESEARCH
# --------------------------------------------------

elif page == "🔎 Medical Research":
    section_header(
        "🔎",
        "Trusted Medical Research",
        "Explore health information retrieved "
        "from MedlinePlus."
    )

    research_query = st.text_input(
        "Search medical topics",
        value="chronic kidney disease"
    )

    if st.button(
        "📚 Search Medical Information",
        type="primary"
    ):
        if not research_query.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Searching MedlinePlus..."):
                result = safe_monitor(
                    "MedicalSearch",
                    "retrieve_medical_information",
                    retrieve_medical_information,
                    research_query
                )

            if result is not None:
                sources = result.get("sources", [])

                if sources:
                    st.success(
                        f"Found {len(sources)} trusted sources."
                    )

                    for source in sources:
                        with st.container(border=True):
                            st.markdown(
                                f"### 📖 {source['title']}"
                            )

                            st.write(
                                source.get(
                                    "content",
                                    "No summary available."
                                )
                            )

                            st.markdown(
                                f"[Read on MedlinePlus]"
                                f"({source['url']})"
                            )
                else:
                    st.warning(
                        "No verified medical sources were retrieved."
                    )


# --------------------------------------------------
# DOCTOR DASHBOARD
# --------------------------------------------------

elif page == "👨‍⚕️ Doctor View":
    section_header(
        "👨‍⚕️",
        "Doctor Workspace",
        "Review fictional specialists and their "
        "simulated available appointment slots."
    )

    doctors = get_doctors()

    st.markdown("### 🩺 Available Specialists")

    for doctor in doctors:
        with st.expander(
            f"👨‍⚕️ {doctor['name']} — "
            f"{doctor['specialization']}"
        ):
            st.write(
                f"**Doctor ID:** {doctor['id']}"
            )

            slots = get_available_slots(
                doctor["id"],
                days=7
            )

            st.metric(
                "Available Slots",
                len(slots)
            )

            if slots:
                st.markdown("**Upcoming availability**")

                for slot in slots[:8]:
                    st.write(f"🕒 {slot}")
            else:
                st.info("No slots available.")


# --------------------------------------------------
# EVALUATION AND MONITORING
# --------------------------------------------------

elif page == "📊 Evaluation & Monitoring":
    section_header(
        "📊",
        "Agent Performance Analytics",
        "Monitor logged tool executions, response "
        "evaluation metrics, and system activity."
    )

    monitoring = get_monitoring_metrics()
    evaluation = get_evaluation_metrics()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "⚙️ Tool Calls",
        monitoring["total_calls"]
    )

    c2.metric(
        "✅ Success Rate",
        f"{monitoring['success_rate']}%"
    )

    c3.metric(
        "⏱️ Average Latency",
        f"{monitoring['average_duration_ms']} ms"
    )

    c4.metric(
        "🧪 Evaluations",
        evaluation["total_evaluations"]
    )

    st.markdown("### 📈 Response Evaluation")

    col1, col2 = st.columns(2)

    col1.metric(
        "Lexical Relevance",
        f"{evaluation['average_relevance']:.3f}"
    )

    col2.metric(
        "Reference Similarity",
        f"{evaluation['average_reference_similarity']:.3f}"
    )

    st.caption(
        "These automated lexical metrics do not "
        "establish clinical accuracy."
    )

    st.markdown("### 📜 Tool Execution Logs")

    logs = get_agent_logs(limit=100)

    show_dataframe(
        logs,
        "No agent execution logs yet."
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        padding:22px 10px;
        color:#64748b;
        font-size:13px;
    ">
        🏥 <b>MediFlow AI</b> — Agentic Healthcare Assistant<br>
        Built with Gemini AI • LangGraph • FAISS • Streamlit<br>
        Educational Capstone Project | Fictional Demo Data Only
    </div>
    """,
    unsafe_allow_html=True
)
