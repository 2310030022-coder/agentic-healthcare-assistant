
import streamlit as st
import pandas as pd
from html import escape

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


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="MediFlow AI | Healthcare Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_custom_style()
initialize_database()

PAGES = [
    "🏠 Dashboard",
    "🤖 AI Healthcare Assistant",
    "📅 Appointments",
    "📋 Medical Records",
    "🧠 FAISS Memory",
    "🔎 Medical Research",
    "👨‍⚕️ Doctor View",
    "📊 Evaluation & Monitoring"
]

if "current_page" not in st.session_state:
    st.session_state.current_page = PAGES[0]


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def section_header(icon, title, description):
    title = escape(title)
    description = escape(description)

    st.markdown(
        f"""
        <div class="section-header">
            <h2>{icon} {title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def run_monitored(module, action, function, *args, **kwargs):
    try:
        return monitor_execution(
            module,
            action,
            function,
            *args,
            **kwargs
        )
    except Exception as exc:
        st.error(f"{action} failed: {exc}")
        return None


def show_table(data, message="No information available."):
    if data:
        st.dataframe(
            pd.DataFrame(data),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(message)


def operation_succeeded(result):
    if isinstance(result, dict):
        return result.get("success", True) is not False

    return result is not False


def show_operation_result(result, success_message):
    if isinstance(result, dict):
        message = result.get("message", success_message)

        if result.get("success", True) is False:
            st.error(message)
            return False

        st.success(message)
        return True

    if result is False:
        st.error("The operation was not completed.")
        return False

    st.success(success_message)
    return True


def change_page(destination):
    st.session_state.current_page = destination


# =====================================================
# HEADER
# =====================================================

st.markdown(
    """
    <div class="main-title">🏥 MediFlow AI</div>
    <div class="subtitle">
        Intelligent Healthcare Task Automation Platform
        • Gemini AI • LangGraph • FAISS RAG
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "🎓 Educational capstone using fictional patient "
    "records and simulated appointments. "
    "Not for real medical care or clinical decisions."
)


# =====================================================
# SIDEBAR NAVIGATION
# =====================================================

with st.sidebar:
    st.markdown("## 🏥 MediFlow AI")
    st.caption("INTELLIGENT HEALTHCARE WORKSPACE")

    st.divider()

    page = st.radio(
        "Explore modules",
        PAGES,
        key="current_page"
    )

    st.divider()
    st.markdown("### 👤 Demo Patient")

    patients = get_patients()

    patient_options = {
        f"{p['name']} • ID {p['id']}": p["id"]
        for p in patients
    }

    if not patient_options:
        st.error("No demo patients found.")
        st.stop()

    selected_patient = st.selectbox(
        "Select patient",
        options=list(patient_options.keys()),
        key="selected_demo_patient"
    )

    patient_id = patient_options[selected_patient]
    patient = get_patient(patient_id)

    if patient:
        st.markdown(f"**Name:** {patient['name']}")
        st.markdown(f"**Age:** {patient['age']} years")
        st.markdown(f"**Patient ID:** {patient['id']}")

    st.caption(
        "Demo patient selection is not authentication. "
        "Use fictional records only."
    )

    st.divider()
    st.caption("✨ Powered by Google Gemini")


# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    render_hero()

    section_header(
        "📊",
        "Healthcare Overview",
        "Explore patient records, simulated bookings, "
        "and intelligent healthcare tools."
    )

    appointments = get_patient_appointments(patient_id)
    history = get_medical_history(patient_id)

    active_appointments = [
        a for a in appointments
        if a.get("status") == "Booked"
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Patients", len(patients))
    col2.metric("👨‍⚕️ Doctors", len(get_doctors()))
    col3.metric("📋 Medical Records", len(history))
    col4.metric(
        "📅 Active Appointments",
        len(active_appointments)
    )

    st.markdown("### ✨ Explore the Platform")

    render_feature_cards()

    st.markdown("### 🏥 Patient Workspace")

    left, right = st.columns([1, 1.5])

    with left:
        st.markdown("#### 👤 Patient Profile")

        with st.container(border=True):
            st.markdown(
                f"### {escape(str(patient['name']))}"
            )
            st.write(f"**Patient ID:** {patient_id}")
            st.write(f"**Age:** {patient['age']} years")
            st.caption("Fictional demonstration patient")

            if st.button(
                "📋 Open Medical Records",
                use_container_width=True
            ):
                change_page("📋 Medical Records")
                st.rerun()

    with right:
        st.markdown("#### 📋 Recent Medical History")
        show_table(
            history[:5],
            "No medical history has been recorded."
        )

    st.markdown("### 📅 Upcoming Appointments")

    show_table(
        active_appointments,
        "No active appointments for this patient."
    )

    if st.button(
        "➕ Book an Appointment",
        type="primary"
    ):
        change_page("📅 Appointments")
        st.rerun()


# =====================================================
# AI HEALTHCARE ASSISTANT
# =====================================================

elif page == "🤖 AI Healthcare Assistant":

    section_header(
        "🤖",
        "Intelligent Healthcare Agent",
        "Use Gemini and LangGraph to coordinate "
        "multi-step fictional healthcare tasks."
    )

    examples = {
        "Kidney Care": (
            "Summarize this patient's medical history, "
            "find available nephrologist appointments, "
            "and research chronic kidney disease."
        ),
        "Heart Care": (
            "Find cardiology appointments and research "
            "trusted information about heart disease."
        ),
        "Patient History": (
            "Summarize the selected patient's "
            "medical history."
        ),
        "General Consultation": (
            "Find a general medicine doctor "
            "for a routine consultation."
        )
    }

    selected_example = st.selectbox(
        "Choose an example",
        list(examples.keys())
    )

    query = st.text_area(
        "Describe your healthcare request",
        value=examples[selected_example],
        height=140
    )

    if st.button(
        "✨ Run AI Healthcare Agent",
        type="primary",
        use_container_width=True
    ):
        if not query.strip():
            st.warning("Please enter a request.")
        else:
            with st.spinner(
                "Gemini is planning and executing..."
            ):
                result = run_monitored(
                    "LangGraph",
                    "run_healthcare_agent",
                    run_healthcare_agent,
                    query,
                    patient_id
                )

            if result is not None:
                st.session_state["agent_result"] = result
                st.session_state["agent_query"] = query
                st.session_state["agent_patient"] = patient_id

    result = st.session_state.get("agent_result")

    if (
        result is not None
        and st.session_state.get("agent_patient") == patient_id
    ):
        st.markdown("### ✨ Agent Response")

        with st.container(border=True):
            st.markdown(
                result.get("response", "No response generated.")
            )

        tab1, tab2, tab3 = st.tabs([
            "🧩 Planning",
            "🔍 Execution Trace",
            "📚 Medical Sources"
        ])

        with tab1:
            st.write(
                result.get("plan", "No plan available.")
            )

        with tab2:
            trace = result.get("execution_trace", [])

            if trace:
                for index, step in enumerate(trace, 1):
                    st.write(f"**{index}.** {step}")
            else:
                st.info("No trace recorded.")

        with tab3:
            sources = result.get("medical_sources", [])

            if sources:
                for source in sources:
                    st.markdown(
                        f"**[{source['title']}]"
                        f"({source['url']})**"
                    )
            else:
                st.info("No medical sources retrieved.")

        st.markdown("### 📊 Evaluate Response")

        if st.button("Evaluate Agent Response"):
            evaluation = run_monitored(
                "Evaluation",
                "evaluate_response",
                evaluate_response,
                st.session_state.get("agent_query", ""),
                result.get("response", "")
            )

            if evaluation is not None:
                st.json(evaluation)
                st.caption(
                    "Lexical scores are not clinical "
                    "accuracy measurements."
                )

    st.divider()

    st.markdown("### 📅 Need to confirm a booking?")

    st.write(
        "The AI can suggest doctors and available slots. "
        "Booking requires your explicit confirmation."
    )

    if st.button("Open Appointment Booking"):
        change_page("📅 Appointments")
        st.rerun()


# =====================================================
# SMART APPOINTMENT BOOKING
# =====================================================

elif page == "📅 Appointments":

    section_header(
        "📅",
        "Smart Appointment Booking",
        "Choose a medical department, select a doctor, "
        "and confirm a simulated appointment."
    )

    doctors = get_doctors()

    departments = sorted({
        d["specialization"]
        for d in doctors
    })

    if not departments:
        st.warning("No medical departments available.")
    else:
        st.markdown("### 🏥 Step 1 — Choose Department")

        department = st.selectbox(
            "Medical Department",
            departments
        )

        matching_doctors = [
            d for d in doctors
            if d["specialization"] == department
        ]

        st.markdown("### 👨‍⚕️ Step 2 — Select Doctor")

        doctor_options = {
            f"{d['name']} — {d['specialization']}": d["id"]
            for d in matching_doctors
        }

        if doctor_options:
            selected_doctor = st.selectbox(
                "Available Doctors",
                list(doctor_options.keys())
            )

            doctor_id = doctor_options[selected_doctor]

            st.markdown("### 🕒 Step 3 — Select Time")

            slots = get_available_slots(
                doctor_id,
                days=7
            )

            if slots:
                selected_slot = st.selectbox(
                    "Available Appointment Slots",
                    slots
                )

                with st.container(border=True):
                    st.markdown("#### 📋 Booking Summary")
                    st.write(f"**Patient:** {patient['name']}")
                    st.write(f"**Department:** {department}")
                    st.write(f"**Doctor:** {selected_doctor}")
                    st.write(f"**Date & Time:** {selected_slot}")

                    confirmed = st.checkbox(
                        "I confirm this fictional appointment."
                    )

                    if st.button(
                        "✅ Confirm Appointment",
                        type="primary",
                        disabled=not confirmed
                    ):
                        result = run_monitored(
                            "Appointments",
                            "book_appointment",
                            book_appointment,
                            patient_id,
                            doctor_id,
                            selected_slot
                        )

                        if result is not None:
                            if show_operation_result(
                                result,
                                "Appointment booked successfully."
                            ):
                                st.rerun()
            else:
                st.warning(
                    "No available slots for this doctor."
                )
        else:
            st.warning("No doctors found in this department.")

    st.divider()
    st.markdown("### 📋 Patient Appointments")

    appointments = get_patient_appointments(patient_id)

    show_table(
        appointments,
        "No appointments found."
    )

    active = [
        a for a in appointments
        if a.get("status") == "Booked"
    ]

    if active:
        st.markdown("### ❌ Cancel Appointment")

        appointment_options = {
            (
                f"#{a['id']} — {a['doctor_name']} "
                f"— {a['appointment_time']}"
            ): a["id"]
            for a in active
        }

        chosen = st.selectbox(
            "Choose appointment",
            list(appointment_options.keys())
        )

        confirm_cancel = st.checkbox(
            "I confirm cancellation of this demo booking."
        )

        if st.button(
            "Cancel Selected Appointment",
            disabled=not confirm_cancel
        ):
            result = run_monitored(
                "Appointments",
                "cancel_appointment",
                cancel_appointment,
                appointment_options[chosen]
            )

            if result is not None:
                if show_operation_result(
                    result,
                    "Appointment cancelled."
                ):
                    st.rerun()


# =====================================================
# ELECTRONIC MEDICAL RECORDS
# =====================================================

elif page == "📋 Medical Records":

    section_header(
        "📋",
        "Electronic Medical Records",
        "Create and update fictional patient records "
        "for the healthcare demonstration."
    )

    history = get_medical_history(patient_id)

    st.markdown("### 🩺 Patient Medical History")

    show_table(
        history,
        "No medical records found."
    )

    st.markdown("### ➕ Add New Medical Record")

    with st.form("add_record"):
        diagnosis = st.text_input(
            "Diagnosis",
            placeholder="Example: Chronic Kidney Disease"
        )

        treatment = st.text_area(
            "Treatment",
            placeholder="Enter fictional treatment information"
        )

        notes = st.text_area(
            "Clinical Notes",
            placeholder="Enter fictional observations"
        )

        submitted = st.form_submit_button(
            "💾 Save Record",
            type="primary"
        )

    if submitted:
        if not diagnosis.strip():
            st.warning("Please enter a diagnosis.")
        else:
            result = run_monitored(
                "MedicalRecords",
                "add_medical_record",
                add_medical_record,
                patient_id,
                diagnosis,
                treatment,
                notes
            )

            if result is not None:
                show_operation_result(
                    result,
                    "Medical record saved."
                )
                st.rerun()

    if history:
        st.divider()
        st.markdown("### ✏️ Update Existing Record")

        record_options = {
            (
                f"Record #{r['id']} — "
                f"{r['diagnosis']}"
            ): r
            for r in history
        }

        selected_record = st.selectbox(
            "Select record",
            list(record_options.keys())
        )

        record = record_options[selected_record]

        with st.form("edit_record"):
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

            update_submitted = st.form_submit_button(
                "Update Record"
            )

        if update_submitted:
            if not new_diagnosis.strip():
                st.warning("Diagnosis cannot be empty.")
            else:
                result = run_monitored(
                    "MedicalRecords",
                    "update_medical_record",
                    update_medical_record,
                    record["id"],
                    new_diagnosis,
                    new_treatment,
                    new_notes
                )

                if result is not None:
                    show_operation_result(
                        result,
                        "Medical record updated."
                    )
                    st.rerun()


# =====================================================
# FAISS MEMORY
# =====================================================

elif page == "🧠 FAISS Memory":

    section_header(
        "🧠",
        "Semantic Patient Memory",
        "Search fictional patient records using "
        "FAISS vector similarity."
    )

    st.markdown(
        f"### 👤 Patient: {patient['name']}"
    )

    query = st.text_input(
        "Search patient memory",
        placeholder="Example: kidney disease history"
    )

    if st.button(
        "🔍 Search FAISS Memory",
        type="primary"
    ):
        if not query.strip():
            st.warning("Enter a search query.")
        else:
            with st.spinner(
                "Retrieving semantic patient memory..."
            ):
                results = run_monitored(
                    "FAISS",
                    "retrieve_patient_memory",
                    retrieve_patient_memory,
                    patient_id,
                    query
                )

            if results is not None:
                if results:
                    for index, item in enumerate(results, 1):
                        with st.container(border=True):
                            st.markdown(
                                f"#### 🧠 Memory Match {index}"
                            )

                            st.write(
                                "**Similarity:**",
                                round(
                                    float(
                                        item.get("similarity", 0)
                                    ),
                                    3
                                )
                            )

                            st.text(
                                item.get("content", "")
                            )
                else:
                    st.info(
                        "No matching patient memory found. "
                        "Try adding a fictional medical record."
                    )


# =====================================================
# MEDICAL RESEARCH
# =====================================================

elif page == "🔎 Medical Research":

    section_header(
        "🔎",
        "Trusted Medical Research",
        "Search for educational health information "
        "from MedlinePlus."
    )

    query = st.text_input(
        "Search medical information",
        value="chronic kidney disease"
    )

    if st.button(
        "📚 Search Medical Information",
        type="primary"
    ):
        if not query.strip():
            st.warning("Enter a medical topic.")
        else:
            with st.spinner("Searching trusted sources..."):
                result = run_monitored(
                    "MedicalSearch",
                    "retrieve_medical_information",
                    retrieve_medical_information,
                    query
                )

            if result is not None:
                sources = result.get("sources", [])

                if sources:
                    st.success(
                        f"Found {len(sources)} sources."
                    )

                    for source in sources:
                        with st.container(border=True):
                            st.markdown(
                                f"### 📖 {source['title']}"
                            )

                            st.write(
                                source.get("content", "")
                            )

                            st.markdown(
                                f"[Read on MedlinePlus]"
                                f"({source['url']})"
                            )
                else:
                    st.warning(
                        "No verified sources retrieved."
                    )


# =====================================================
# DOCTOR VIEW
# =====================================================

elif page == "👨‍⚕️ Doctor View":

    section_header(
        "👨‍⚕️",
        "Doctor Workspace",
        "Explore fictional medical specialists "
        "and simulated appointment availability."
    )

    doctors = get_doctors()

    for doctor in doctors:
        with st.expander(
            f"👨‍⚕️ {doctor['name']} — "
            f"{doctor['specialization']}"
        ):
            st.write(f"**Doctor ID:** {doctor['id']}")

            slots = get_available_slots(
                doctor["id"],
                days=7
            )

            st.metric(
                "Available Slots",
                len(slots)
            )

            if slots:
                st.markdown("**Upcoming available slots**")

                for slot in slots[:8]:
                    st.write(f"🕒 {slot}")
            else:
                st.info("No available slots.")


# =====================================================
# EVALUATION AND MONITORING
# =====================================================

elif page == "📊 Evaluation & Monitoring":

    section_header(
        "📊",
        "Agent Analytics",
        "Monitor tool execution, response evaluation, "
        "and performance metrics."
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

    st.markdown("### 📈 Evaluation Results")

    left, right = st.columns(2)

    left.metric(
        "Lexical Relevance",
        f"{evaluation['average_relevance']:.3f}"
    )

    right.metric(
        "Reference Similarity",
        f"{evaluation['average_reference_similarity']:.3f}"
    )

    st.caption(
        "These metrics measure lexical similarity, "
        "not clinical accuracy."
    )

    st.markdown("### 📜 Tool Execution Logs")

    logs = get_agent_logs(limit=100)

    show_table(
        logs,
        "No execution logs recorded yet."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div class="footer-text">
        🏥 <b>MediFlow AI</b><br>
        Gemini AI • LangGraph • FAISS • Streamlit<br>
        Educational Healthcare Capstone |
        Fictional Data Only
    </div>
    """,
    unsafe_allow_html=True
)
