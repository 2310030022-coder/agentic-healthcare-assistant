
import streamlit as st
import pandas as pd

from healthcare.ui_style import (
    apply_custom_style,
    render_hero,
    render_feature_cards
)
from healthcare.database import initialize_database, create_patient
from healthcare.records import (
    get_patients,
    get_patient,
    get_medical_history,
    add_medical_record,
    update_medical_record,
    generate_history_context
)
from healthcare.appointments import (
    get_doctors,
    get_available_slots,
    book_appointment,
    get_patient_appointments,
    cancel_appointment
)
from healthcare.medical_search import retrieve_medical_information
from healthcare.config import generate_ai_response


# =====================================================
# APP SETUP
# =====================================================

st.set_page_config(
    page_title="MediFlow AI",
    page_icon="🏥",
    layout="wide"
)

apply_custom_style()
initialize_database()

PAGES = [
    "🏠 Dashboard",
    "👤 Patients",
    "📅 Appointments",
    "📋 Medical Records",
    "🩺 History Summary",
    "🔎 Medical Research",
    "🤖 AI Healthcare Assistant",
    "🧠 FAISS Memory",
    "📊 Evaluation & Monitoring"
]

# Apply navigation before creating sidebar radio.
if "_next_page" in st.session_state:
    st.session_state["page"] = st.session_state.pop("_next_page")


def navigate(destination):
    st.session_state["_next_page"] = destination
    st.rerun()


def show_table(rows, empty_message="No records found."):
    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info(empty_message)


def show_result(result, success_message):
    if isinstance(result, dict):
        if result.get("success") is False:
            st.error(result.get("message", "Operation failed."))
            return False

        st.success(result.get("message", success_message))
        return True

    if result is False:
        st.error("Operation failed.")
        return False

    st.success(success_message)
    return True


DEPARTMENT_GUIDE = {
    "Kidney disease or kidney-related concerns": "Nephrology",
    "Heart or blood pressure concerns": "Cardiology",
    "Headaches or nerve-related concerns": "Neurology",
    "Bones, joints or injuries": "Orthopedics",
    "Skin conditions or rashes": "Dermatology",
    "Stomach, digestion or liver concerns": "Gastroenterology",
    "Diabetes, thyroid or hormone concerns": "Endocrinology",
    "Breathing or lung concerns": "Pulmonology",
    "Ear, nose or throat concerns": "ENT",
    "Eye or vision concerns": "Ophthalmology",
    "Women's reproductive health": "Gynecology",
    "Mental health concerns": "Psychiatry",
    "Children's health": "Pediatrics",
    "Routine consultation or unsure": "General Medicine"
}


# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:
    st.title("🏥 MediFlow AI")
    st.caption("INTELLIGENT HEALTHCARE WORKSPACE")

    page = st.radio(
        "Explore modules",
        PAGES,
        key="page"
    )

    st.divider()
    st.subheader("👤 Demo Patient")

    patients = get_patients()

    if not patients:
        st.error("No demo patients available.")
        st.stop()

    patient_options = {
        f"{p['name']} • ID {p['id']}": p["id"]
        for p in patients
    }

    selected_patient = st.selectbox(
        "Select patient",
        list(patient_options.keys()),
        key="selected_patient"
    )

    patient_id = patient_options[selected_patient]
    patient = get_patient(patient_id)

    st.write(f"**Name:** {patient['name']}")
    st.write(f"**Age:** {patient['age']} years")

    if st.button(
        "➕ Register New Patient",
        use_container_width=True
    ):
        navigate("👤 Patients")

    st.divider()
    st.caption("Fictional patient records only.")


# =====================================================
# MAIN HEADER
# =====================================================

st.title("🏥 MediFlow AI")

st.caption(
    "Agentic Healthcare Automation • Gemini AI • "
    "LangGraph • FAISS • Streamlit"
)

st.info(
    "🎓 Educational capstone project. All patients, "
    "doctors and appointments are fictional. "
    "Not intended for real medical decisions."
)


# =====================================================
# DASHBOARD
# =====================================================

if page == "🏠 Dashboard":

    render_hero()

    appointments = get_patient_appointments(patient_id)
    history = get_medical_history(patient_id)

    active_bookings = [
        a for a in appointments
        if a.get("status") == "Booked"
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("👥 Patients", len(patients))
    col2.metric("👨‍⚕️ Doctors", len(get_doctors()))
    col3.metric("📋 Medical Records", len(history))
    col4.metric("📅 Active Bookings", len(active_bookings))

    st.markdown("## ✨ Explore the Platform")

    render_feature_cards()

    st.markdown("## 👤 Selected Patient")

    with st.container(border=True):
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Patient ID:** {patient_id}")

    st.markdown("## 📋 Recent Medical History")

    show_table(
        history[:5],
        "No medical history yet."
    )

    if st.button(
        "📅 Book an Appointment",
        type="primary"
    ):
        navigate("📅 Appointments")


# =====================================================
# PATIENT REGISTRATION
# =====================================================

elif page == "👤 Patients":

    st.header("👤 Patient Registration")

    st.write(
        "Register a fictional patient and then select "
        "that patient from the sidebar."
    )

    with st.form("patient_registration", clear_on_submit=True):

        name = st.text_input(
            "Patient Full Name",
            placeholder="Example: Riya Sharma"
        )

        age = st.number_input(
            "Patient Age",
            min_value=0,
            max_value=120,
            value=30,
            step=1
        )

        submitted = st.form_submit_button(
            "➕ Register Patient",
            type="primary"
        )

    if submitted:
        try:
            new_id = create_patient(name, age)

            st.success(
                f"Patient {name.strip()} registered. "
                f"Patient ID: {new_id}"
            )

            st.info(
                "Select the new patient from the sidebar."
            )

        except Exception as exc:
            st.error(f"Registration failed: {exc}")

    st.subheader("Registered Demo Patients")

    show_table(get_patients())


# =====================================================
# SMART APPOINTMENT BOOKING
# =====================================================

elif page == "📅 Appointments":

    st.header("📅 Smart Appointment Booking")

    st.write(
        f"**Selected Patient:** {patient['name']}"
    )

    st.subheader("Step 1 — Describe Patient Concern")

    concern = st.selectbox(
        "What does the patient need help with?",
        list(DEPARTMENT_GUIDE.keys())
    )

    suggested_department = DEPARTMENT_GUIDE[concern]

    st.info(
        f"Suggested Department: "
        f"**{suggested_department}**"
    )

    st.caption(
        "Department suggestions are general educational "
        "guidance, not diagnoses. Serious or sudden "
        "symptoms may require urgent medical care."
    )

    st.subheader("Step 2 — Select Medical Department")

    doctors = get_doctors()

    departments = sorted({
        d["specialization"]
        for d in doctors
    })

    if departments:

        default_index = (
            departments.index(suggested_department)
            if suggested_department in departments
            else 0
        )

        department = st.selectbox(
            "Choose Department",
            departments,
            index=default_index,
            key=f"department_{concern}"
        )

        matching_doctors = [
            d for d in doctors
            if d["specialization"] == department
        ]

        st.subheader("Step 3 — Select Doctor")

        if matching_doctors:

            doctor_options = {
                f"{d['name']} — {d['specialization']}": d["id"]
                for d in matching_doctors
            }

            selected_doctor = st.selectbox(
                "Available Doctors",
                list(doctor_options.keys())
            )

            doctor_id = doctor_options[selected_doctor]

            st.subheader("Step 4 — Select Appointment Slot")

            available_slots = get_available_slots(
                doctor_id,
                days=7
            )

            if available_slots:

                selected_slot = st.selectbox(
                    "Available Date and Time",
                    available_slots
                )

                st.subheader("Step 5 — Confirm Booking")

                with st.container(border=True):

                    st.write(
                        f"**Patient:** {patient['name']}"
                    )

                    st.write(
                        f"**Department:** {department}"
                    )

                    st.write(
                        f"**Doctor:** {selected_doctor}"
                    )

                    st.write(
                        f"**Appointment:** {selected_slot}"
                    )

                    confirmed = st.checkbox(
                        "I confirm this simulated appointment."
                    )

                    if st.button(
                        "✅ Confirm Appointment",
                        type="primary",
                        disabled=not confirmed
                    ):
                        try:
                            result = book_appointment(
                                patient_id,
                                doctor_id,
                                selected_slot
                            )

                            if show_result(
                                result,
                                "Appointment booked successfully."
                            ):
                                st.rerun()

                        except Exception as exc:
                            st.error(
                                f"Booking failed: {exc}"
                            )

            else:
                st.warning(
                    "No slots available for this doctor "
                    "in the next seven days."
                )

        else:
            st.warning(
                "No doctors available in this department."
            )

    else:
        st.error("No departments available.")

    st.divider()

    st.subheader("📋 Patient Appointment History")

    bookings = get_patient_appointments(patient_id)

    show_table(
        bookings,
        "No appointments found."
    )

    active = [
        a for a in bookings
        if a.get("status") == "Booked"
    ]

    if active:

        booking_options = {
            (
                f"#{a['id']} — "
                f"{a.get('doctor_name', 'Doctor')} — "
                f"{a['appointment_time']}"
            ): a["id"]
            for a in active
        }

        selected_booking = st.selectbox(
            "Select Appointment to Cancel",
            list(booking_options.keys())
        )

        confirm_cancellation = st.checkbox(
            "I confirm cancellation of this demo appointment."
        )

        if st.button(
            "❌ Cancel Appointment",
            disabled=not confirm_cancellation
        ):
            try:
                result = cancel_appointment(
                    booking_options[selected_booking]
                )

                if show_result(
                    result,
                    "Appointment cancelled."
                ):
                    st.rerun()

            except Exception as exc:
                st.error(str(exc))


# =====================================================
# MEDICAL RECORD MANAGEMENT
# =====================================================

elif page == "📋 Medical Records":

    st.header("📋 Electronic Medical Records")

    st.write(
        f"**Patient:** {patient['name']}"
    )

    records = get_medical_history(patient_id)

    st.subheader("Existing Medical History")

    show_table(
        records,
        "No medical records found."
    )

    st.subheader("➕ Add Medical Record")

    with st.form("add_medical_record"):

        diagnosis = st.text_input(
            "Diagnosis or Condition"
        )

        treatment = st.text_area(
            "Treatment Information"
        )

        notes = st.text_area(
            "Additional Medical Notes"
        )

        submitted = st.form_submit_button(
            "💾 Save Medical Record",
            type="primary"
        )

    if submitted:

        if not diagnosis.strip():
            st.warning("Please enter a diagnosis.")

        else:
            try:
                add_medical_record(
                    patient_id,
                    diagnosis.strip(),
                    treatment,
                    notes
                )

                st.success("Medical record added.")
                st.rerun()

            except Exception as exc:
                st.error(str(exc))

    if records:

        st.divider()

        st.subheader("✏️ Update Medical Record")

        record_options = {
            f"#{r['id']} — {r['diagnosis']}": r
            for r in records
        }

        selected_record = st.selectbox(
            "Select Record",
            list(record_options.keys())
        )

        record = record_options[selected_record]

        with st.form("update_medical_record"):

            new_diagnosis = st.text_input(
                "Diagnosis",
                value=record.get("diagnosis") or ""
            )

            new_treatment = st.text_area(
                "Treatment",
                value=record.get("treatment") or ""
            )

            new_notes = st.text_area(
                "Medical Notes",
                value=record.get("notes") or ""
            )

            update_submitted = st.form_submit_button(
                "Update Record"
            )

        if update_submitted:

            if not new_diagnosis.strip():
                st.warning("Diagnosis cannot be empty.")

            else:
                try:
                    update_medical_record(
                        record["id"],
                        new_diagnosis,
                        new_treatment,
                        new_notes
                    )

                    st.success("Record updated.")
                    st.rerun()

                except Exception as exc:
                    st.error(str(exc))


# =====================================================
# AI MEDICAL HISTORY SUMMARY
# =====================================================

elif page == "🩺 History Summary":

    st.header("🩺 AI Medical History Summary")

    st.write(
        f"**Selected Patient:** {patient['name']}"
    )

    records = get_medical_history(patient_id)

    show_table(
        records,
        "No medical history available."
    )

    if st.button(
        "✨ Generate AI History Summary",
        type="primary",
        disabled=not bool(records)
    ):

        with st.spinner(
            "Gemini is summarizing patient history..."
        ):

            try:
                history_context = generate_history_context(
                    patient_id
                )

                prompt = (
                    "Summarize ONLY the supplied fictional "
                    "patient history. Include documented "
                    "diagnoses, treatments and notes. "
                    "Do not invent missing details, "
                    "diagnose, or prescribe. "
                    "Clearly identify missing information.\n\n"
                    + history_context
                )

                summary = generate_ai_response(prompt)

                st.session_state["history_summary"] = (
                    patient_id,
                    summary
                )

            except Exception as exc:
                st.error(
                    f"History summary failed: {exc}"
                )

    saved_summary = st.session_state.get(
        "history_summary"
    )

    if (
        saved_summary
        and saved_summary[0] == patient_id
    ):

        st.subheader("Generated Patient Summary")

        st.write(saved_summary[1])

        st.caption(
            "AI-generated educational summary. "
            "Verify against the original records."
        )


# =====================================================
# TRUSTED MEDICAL INFORMATION SEARCH
# =====================================================

elif page == "🔎 Medical Research":

    st.header("🔎 Trusted Medical Information Search")

    st.write(
        "Search educational medical information "
        "from MedlinePlus."
    )

    topic = st.text_input(
        "Enter Disease or Medical Topic",
        value="chronic kidney disease"
    )

    if st.button(
        "🔍 Search Medical Information",
        type="primary"
    ):

        if not topic.strip():
            st.warning("Please enter a medical topic.")

        else:
            with st.spinner(
                "Searching trusted medical sources..."
            ):

                try:
                    results = retrieve_medical_information(
                        topic
                    )

                    st.session_state["medical_research"] = (
                        topic,
                        results
                    )

                except Exception as exc:
                    st.error(
                        f"Medical search failed: {exc}"
                    )

    research = st.session_state.get(
        "medical_research"
    )

    if research and research[0] == topic:

        sources = research[1].get(
            "sources",
            []
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
                            "Medical Information"
                        )
                    )

                    st.write(
                        source.get(
                            "content",
                            "No preview available."
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
                            url
                        )

        else:
            st.warning(
                "No verified sources were returned. "
                "Try a broader medical search term."
            )


# =====================================================
# LANGGRAPH AI HEALTHCARE ASSISTANT
# =====================================================

elif page == "🤖 AI Healthcare Assistant":

    st.header("🤖 Intelligent Healthcare Agent")

    st.write(
        "Enter a multi-step healthcare request "
        "to explore AI planning and tool execution."
    )

    query = st.text_area(
        "Enter Healthcare Request",
        value=(
            "Summarize patient medical history, "
            "find nephrology appointments, "
            "and research chronic kidney disease."
        ),
        height=140
    )

    if st.button(
        "✨ Run Healthcare Agent",
        type="primary"
    ):

        if not query.strip():
            st.warning("Enter a request.")

        else:
            with st.spinner(
                "Running LangGraph healthcare agent..."
            ):

                try:
                    from healthcare.agent import (
                        run_healthcare_agent
                    )

                    result = run_healthcare_agent(
                        query,
                        patient_id
                    )

                    st.session_state["agent_result"] = (
                        patient_id,
                        result
                    )

                except Exception as exc:
                    st.error(
                        f"AI agent failed: {exc}"
                    )

    saved_result = st.session_state.get(
        "agent_result"
    )

    if (
        saved_result
        and saved_result[0] == patient_id
    ):

        result = saved_result[1]

        st.subheader("🤖 Agent Response")

        st.write(
            result.get(
                "response",
                "No response returned."
            )
        )

        with st.expander("🧩 Agent Planning"):
            st.write(
                result.get(
                    "plan",
                    "No plan available."
                )
            )

        with st.expander("🔍 Execution Trace"):
            st.write(
                result.get(
                    "execution_trace",
                    []
                )
            )

        with st.expander("📚 Medical Sources"):
            st.write(
                result.get(
                    "medical_sources",
                    []
                )
            )

    if st.button(
        "📅 Proceed to Appointment Booking"
    ):
        navigate("📅 Appointments")


# =====================================================
# FAISS SEMANTIC MEMORY
# =====================================================

elif page == "🧠 FAISS Memory":

    st.header("🧠 Semantic Patient Memory")

    st.write(
        f"**Patient:** {patient['name']}"
    )

    query = st.text_input(
        "Search Patient Memory",
        placeholder="Example: kidney disease history"
    )

    if st.button(
        "🔍 Search Vector Memory",
        type="primary"
    ):

        if not query.strip():
            st.warning("Enter a search query.")

        else:
            with st.spinner(
                "Searching FAISS vector memory..."
            ):

                try:
                    from healthcare.memory import (
                        retrieve_patient_memory
                    )

                    results = retrieve_patient_memory(
                        patient_id,
                        query
                    )

                    if results:

                        for index, item in enumerate(
                            results,
                            1
                        ):

                            with st.container(border=True):

                                st.markdown(
                                    f"### Memory Match {index}"
                                )

                                st.write(
                                    item.get(
                                        "content",
                                        ""
                                    )
                                )

                                similarity = float(
                                    item.get(
                                        "similarity",
                                        0
                                    )
                                )

                                st.caption(
                                    f"Similarity: {similarity:.3f}"
                                )

                    else:
                        st.info(
                            "No matching memory found."
                        )

                except Exception as exc:
                    st.error(
                        f"FAISS search failed: {exc}"
                    )


# =====================================================
# EVALUATION AND MONITORING
# =====================================================

elif page == "📊 Evaluation & Monitoring":

    st.header("📊 Agent Evaluation and Monitoring")

    try:
        from healthcare.monitoring import (
            get_agent_logs,
            get_monitoring_metrics
        )

        st.subheader("Monitoring Metrics")

        monitoring_metrics = get_monitoring_metrics()

        st.json(monitoring_metrics)

        st.subheader("Agent Execution Logs")

        logs = get_agent_logs(limit=100)

        show_table(
            logs,
            "No execution logs found."
        )

    except Exception as exc:
        st.error(
            f"Monitoring unavailable: {exc}"
        )

    try:
        from healthcare.evaluation import (
            get_evaluation_metrics
        )

        st.subheader("Model Evaluation Metrics")

        evaluation_metrics = get_evaluation_metrics()

        st.json(evaluation_metrics)

    except Exception as exc:
        st.error(
            f"Evaluation unavailable: {exc}"
        )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.markdown(
    """
    <div class="footer">
        🏥 MediFlow AI<br>
        Agentic Healthcare Assistant<br>
        Gemini AI • LangGraph • FAISS • Streamlit<br>
        Educational Capstone Project
    </div>
    """,
    unsafe_allow_html=True
)
