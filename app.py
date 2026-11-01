
import streamlit as st
import pandas as pd

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


st.set_page_config(
    page_title="Agentic Healthcare Assistant",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 2.3rem;
    font-weight: 750;
    color: #126b8a;
}
.subtitle {
    color: #64748b;
    font-size: 1rem;
}
div[data-testid="stMetric"] {
    border: 1px solid #dbe5eb;
    border-radius: 12px;
    padding: 14px;
}
</style>
""", unsafe_allow_html=True)


initialize_database()

st.markdown(
    '<div class="main-title">🏥 Agentic Healthcare Assistant</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">'
    'Gemini AI • LangGraph • FAISS RAG • Medical Task Automation'
    '</div>',
    unsafe_allow_html=True
)

st.info(
    "Educational demonstration using fictional patient data "
    "and simulated doctor schedules. Not for diagnosis, "
    "medical decisions, or real hospital bookings."
)

patients = get_patients()
patient_options = {
    f"{p['name']} (ID: {p['id']})": p["id"]
    for p in patients
}

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select module",
        [
            "Dashboard",
            "AI Healthcare Assistant",
            "Appointments",
            "Medical Records",
            "FAISS Memory",
            "Medical Research",
            "Doctor View",
            "Evaluation & Monitoring"
        ]
    )

    st.divider()
    st.subheader("Demo Patient")

    selected_label = st.selectbox(
        "Choose patient",
        list(patient_options.keys())
    )

    patient_id = patient_options[selected_label]

    st.caption(
        "Demo selection only. This is not authentication."
    )


if page == "Dashboard":
    st.header("Healthcare Overview")

    appointments = get_patient_appointments(patient_id)
    history = get_medical_history(patient_id)

    active = sum(
        1 for a in appointments
        if a["status"] == "Booked"
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Registered Patients", len(patients))
    c2.metric("Available Doctors", len(get_doctors()))
    c3.metric("Patient Records", len(history))
    c4.metric("Active Appointments", active)

    st.subheader("Selected Patient")

    patient = get_patient(patient_id)

    if patient:
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Patient ID:** {patient['id']}")

    st.subheader("Recent Medical Records")

    if history:
        st.dataframe(
            pd.DataFrame(history),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No medical records available.")


elif page == "AI Healthcare Assistant":
    st.header("Gemini-Powered Healthcare Agent")

    st.write(
        "Enter a multi-step healthcare request. "
        "The agent will create a plan, retrieve relevant "
        "records, search doctor availability, and retrieve "
        "trusted medical information when requested."
    )

    example = (
        "Summarize this patient's medical history, "
        "find a nephrologist appointment, and search "
        "for information about chronic kidney disease."
    )

    query = st.text_area(
        "Your healthcare request",
        value=example,
        height=130
    )

    if st.button("Run Healthcare Agent", type="primary"):
        if not query.strip():
            st.warning("Please enter a request.")
        else:
            with st.spinner("Executing LangGraph workflow..."):
                try:
                    result = monitor_execution(
                        "LangGraph",
                        "run_healthcare_agent",
                        run_healthcare_agent,
                        query,
                        patient_id
                    )

                    st.session_state["last_agent_result"] = result
                    st.session_state["last_query"] = query

                except Exception as exc:
                    st.error(
                        "Agent execution failed: "
                        + str(exc)
                    )

    result = st.session_state.get("last_agent_result")

    if result:
        st.subheader("AI Response")
        st.markdown(result.get("response", ""))

        with st.expander("Agent Planning Breakdown"):
            st.write(result.get("plan", ""))

        with st.expander("Execution Trace"):
            for step in result.get("execution_trace", []):
                st.write("✓", step)

        with st.expander("Retrieved Medical Sources"):
            sources = result.get("medical_sources", [])

            if sources:
                for source in sources:
                    st.markdown(
                        f"**{source['title']}**"
                    )
                    st.write(source["url"])
            else:
                st.info("No sources retrieved.")

        if st.button("Evaluate This Response"):
            metrics = evaluate_response(
                st.session_state.get("last_query", ""),
                result.get("response", "")
            )
            st.json(metrics)


elif page == "Appointments":
    st.header("Doctor Appointment Booking")

    doctors = get_doctors()

    doctor_labels = {
        f"{d['name']} — {d['specialization']}": d["id"]
        for d in doctors
    }

    doctor_label = st.selectbox(
        "Select doctor",
        list(doctor_labels.keys())
    )

    doctor_id = doctor_labels[doctor_label]

    slots = get_available_slots(doctor_id)

    if slots:
        selected_slot = st.selectbox(
            "Available appointment slots",
            slots
        )

        if st.button("Confirm Appointment", type="primary"):
            result = monitor_execution(
                "Appointments",
                "book_appointment",
                book_appointment,
                patient_id,
                doctor_id,
                selected_slot
            )

            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])
    else:
        st.warning("No available slots found.")

    st.divider()
    st.subheader("Patient Appointments")

    appointments = get_patient_appointments(patient_id)

    if appointments:
        st.dataframe(
            pd.DataFrame(appointments),
            use_container_width=True,
            hide_index=True
        )

        active = [
            a for a in appointments
            if a["status"] == "Booked"
        ]

        if active:
            appointment_ids = {
                (
                    f"#{a['id']} — {a['doctor_name']} "
                    f"({a['appointment_time']})"
                ): a["id"]
                for a in active
            }

            selected = st.selectbox(
                "Select appointment to cancel",
                list(appointment_ids.keys())
            )

            if st.button("Cancel Selected Appointment"):
                result = monitor_execution(
                    "Appointments",
                    "cancel_appointment",
                    cancel_appointment,
                    appointment_ids[selected]
                )

                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])
    else:
        st.info("No appointments found.")


elif page == "Medical Records":
    st.header("Patient Medical Records")

    history = get_medical_history(patient_id)

    if history:
        st.dataframe(
            pd.DataFrame(history),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No medical history recorded.")

    st.subheader("Add New Medical Record")

    with st.form("add_record"):
        diagnosis = st.text_input("Diagnosis")
        treatment = st.text_area("Treatment")
        notes = st.text_area("Clinical Notes")

        submitted = st.form_submit_button(
            "Save Medical Record"
        )

        if submitted:
            result = monitor_execution(
                "MedicalRecords",
                "add_medical_record",
                add_medical_record,
                patient_id,
                diagnosis,
                treatment,
                notes
            )

            if result["success"]:
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])

    if history:
        st.divider()
        st.subheader("Update Existing Record")

        record_ids = [r["id"] for r in history]

        selected_id = st.selectbox(
            "Select record ID",
            record_ids
        )

        record = next(
            r for r in history
            if r["id"] == selected_id
        )

        with st.form("update_record"):
            new_diagnosis = st.text_input(
                "Update Diagnosis",
                value=record["diagnosis"]
            )

            new_treatment = st.text_area(
                "Update Treatment",
                value=record["treatment"] or ""
            )

            new_notes = st.text_area(
                "Update Notes",
                value=record["notes"] or ""
            )

            if st.form_submit_button("Update Record"):
                result = monitor_execution(
                    "MedicalRecords",
                    "update_medical_record",
                    update_medical_record,
                    selected_id,
                    new_diagnosis,
                    new_treatment,
                    new_notes
                )

                if result["success"]:
                    st.success(result["message"])
                    st.rerun()
                else:
                    st.error(result["message"])


elif page == "FAISS Memory":
    st.header("Semantic Patient Memory")

    query = st.text_input(
        "Search patient history",
        placeholder="Example: kidney disease treatment"
    )

    if st.button("Search FAISS Memory"):
        if not query.strip():
            st.warning("Enter a search query.")
        else:
            with st.spinner("Searching vector memory..."):
                results = monitor_execution(
                    "FAISS",
                    "retrieve_patient_memory",
                    retrieve_patient_memory,
                    patient_id,
                    query
                )

            if results:
                for item in results:
                    with st.expander(
                        f"Record #{item['record_id']} "
                        f"— Similarity {item['similarity']}"
                    ):
                        st.text(item["content"])
            else:
                st.info("No matching records found.")


elif page == "Medical Research":
    st.header("Trusted Medical Information")

    query = st.text_input(
        "Search disease information",
        value="chronic kidney disease"
    )

    if st.button("Search MedlinePlus"):
        with st.spinner("Retrieving medical information..."):
            result = monitor_execution(
                "MedicalSearch",
                "retrieve_medical_information",
                retrieve_medical_information,
                query
            )

        if result["success"]:
            for source in result["sources"]:
                st.subheader(source["title"])
                st.write(source["content"])
                st.markdown(
                    f"[Read trusted source]({source['url']})"
                )
        else:
            st.warning(
                "No trusted medical results were retrieved."
            )


elif page == "Doctor View":
    st.header("Doctor Dashboard")

    doctors = get_doctors()

    for doctor in doctors:
        with st.expander(
            f"{doctor['name']} — {doctor['specialization']}"
        ):
            st.write(f"Doctor ID: {doctor['id']}")

            slots = get_available_slots(
                doctor["id"], days=7
            )

            st.metric(
                "Available Slots (7 days)",
                len(slots)
            )

            if slots:
                st.write("Upcoming available slots:")
                st.write(slots[:10])


elif page == "Evaluation & Monitoring":
    st.header("LLMOps Evaluation Dashboard")

    monitoring = get_monitoring_metrics()
    evaluation = get_evaluation_metrics()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Tool Calls",
        monitoring["total_calls"]
    )
    c2.metric(
        "Tool Success Rate",
        f"{monitoring['success_rate']}%"
    )
    c3.metric(
        "Average Latency",
        f"{monitoring['average_duration_ms']} ms"
    )
    c4.metric(
        "Evaluated Responses",
        evaluation["total_evaluations"]
    )

    st.subheader("Evaluation Metrics")

    st.write(
        "Average lexical relevance:",
        evaluation["average_relevance"]
    )

    st.write(
        "Average reference similarity:",
        evaluation["average_reference_similarity"]
    )

    st.caption(
        "Lexical overlap metrics do not prove "
        "medical correctness or factual accuracy."
    )

    st.subheader("Agent Tool Execution Logs")

    logs = get_agent_logs()

    if logs:
        st.dataframe(
            pd.DataFrame(logs),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No agent logs recorded yet.")


st.divider()

st.caption(
    "Agentic Healthcare Assistant | Educational Capstone | "
    "Gemini + LangGraph + FAISS + Streamlit"
)
