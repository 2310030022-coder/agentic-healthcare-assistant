
import streamlit as st
import pandas as pd

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


# ======================================================
# APP CONFIGURATION
# ======================================================

st.set_page_config(
    page_title="MediFlow AI | Healthcare Management",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_custom_style()
initialize_database()


# ======================================================
# DOCTOR PROFILE IMAGES
# Illustrative photographs, not the actual named doctors.
# ======================================================

DOCTOR_IMAGES = {
    "Nephrology":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=500&fit=crop",
    "Cardiology":
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=500&fit=crop",
    "Neurology":
        "https://images.unsplash.com/photo-1594824476967-48c8b964273f?w=500&fit=crop",
    "Orthopedics":
        "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=500&fit=crop",
    "Dermatology":
        "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=500&fit=crop",
    "General Medicine":
        "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?w=500&fit=crop",
}

DEFAULT_DOCTOR_IMAGE = (
    "https://images.unsplash.com/photo-1582750433449-648ed127bb54?w=500&fit=crop"
)


# ======================================================
# DATABASE HELPERS
# ======================================================

def create_patient(name, age):
    name = name.strip()

    if len(name) < 2:
        raise ValueError("Enter a valid patient name.")

    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO patients (name, age) VALUES (?, ?)",
            (name, int(age)),
        )
        conn.commit()
        return cursor.lastrowid


def seed_doctors():
    doctors = [
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

        for name, specialty in doctors:
            if (name, specialty) not in existing:
                conn.execute(
                    """
                    INSERT INTO doctors (name, specialization)
                    VALUES (?, ?)
                    """,
                    (name, specialty),
                )

        conn.commit()


seed_doctors()


# ======================================================
# HELPERS
# ======================================================

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


def as_dicts(rows):
    return [dict(row) for row in rows]


def show_table(rows, message="No records available."):
    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info(message)


def navigate(destination):
    st.session_state["_next_page"] = destination
    st.rerun()


def success_notification(message):
    st.session_state["_success_message"] = message
    st.rerun()


def result_success(result):
    if isinstance(result, dict):
        return result.get("success", True)
    return result is not False


def result_error(result):
    if isinstance(result, dict):
        return result.get("message", "Operation failed.")
    return "Operation failed."


DEPARTMENT_GUIDE = {
    "Kidney or urinary concerns": "Nephrology",
    "Heart concerns": "Cardiology",
    "Headache or neurological concerns": "Neurology",
    "Bones and joints": "Orthopedics",
    "Skin or hair concerns": "Dermatology",
    "Digestive concerns": "Gastroenterology",
    "Diabetes or thyroid concerns": "Endocrinology",
    "Breathing concerns": "Pulmonology",
    "Ear, nose or throat": "ENT",
    "Eye or vision concerns": "Ophthalmology",
    "Women's health": "Gynecology",
    "Mental health": "Psychiatry",
    "Children's health": "Pediatrics",
    "General consultation": "General Medicine",
}


# ======================================================
# NAVIGATION STATE
# ======================================================

if "_next_page" in st.session_state:
    st.session_state["page"] = st.session_state.pop(
        "_next_page"
    )


# ======================================================
# SIDEBAR
# ======================================================

with st.sidebar:
    st.title("🏥 MediFlow AI")
    st.caption("INTELLIGENT HEALTHCARE WORKSPACE")

    page = st.radio(
        "Explore Modules",
        PAGES,
        key="page",
    )

    st.divider()
    st.subheader("👤 Patient Workspace")

    patients = as_dicts(get_patients())

    patient_id = None
    patient = None

    if patients:
        patient_options = {
            f"{p['name']} • ID {p['id']}": p["id"]
            for p in patients
        }

        selected_label = st.selectbox(
            "Select Patient",
            list(patient_options.keys()),
            key="patient_selector",
        )

        patient_id = patient_options[selected_label]
        patient = get_patient(patient_id)

        if patient:
            st.write(f"**Name:** {patient['name']}")
            st.write(f"**Age:** {patient['age']} years")

    if st.button(
        "➕ Register New Patient",
        use_container_width=True,
        key="sidebar_register",
    ):
        navigate("👤 Patients")

    st.divider()
    st.caption("✨ Powered by Google Gemini")


# ======================================================
# NOTIFICATIONS
# ======================================================

if "_success_message" in st.session_state:
    message = st.session_state.pop("_success_message")
    st.toast(message, icon="✅")
    st.success(message)


# ======================================================
# MAIN HEADER
# ======================================================

st.title("🏥 MediFlow AI")
st.caption(
    "Intelligent Healthcare Management Platform • "
    "Gemini AI • LangGraph • FAISS"
)


# ======================================================
# DASHBOARD
# ======================================================

if page == "🏠 Dashboard":

    # Use a native hero to avoid raw HTML rendering.
    with st.container(border=True):
        st.caption("✨ SMART HEALTHCARE WORKSPACE")
        st.header("Smarter Care. Seamless Coordination.")
        st.write(
            "Manage patient profiles, coordinate appointments, "
            "explore medical specialties, access records, "
            "and use intelligent healthcare tools."
        )

    doctors = as_dicts(get_doctors())

    history = (
        as_dicts(get_medical_history(patient_id))
        if patient_id is not None else []
    )

    bookings = (
        as_dicts(get_patient_appointments(patient_id))
        if patient_id is not None else []
    )

    active = [
        b for b in bookings
        if b.get("status") == "Booked"
    ]

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("👥 Patients", len(patients))
    c2.metric("👨‍⚕️ Doctors", len(doctors))
    c3.metric("📋 Records", len(history))
    c4.metric("📅 Appointments", len(active))

    st.subheader("✨ Explore the Platform")

    render_feature_cards()

    st.subheader("🚀 Quick Actions")

    a, b, c = st.columns(3)

    with a:
        if st.button(
            "➕ Add Patient",
            use_container_width=True,
        ):
            navigate("👤 Patients")

    with b:
        if st.button(
            "📅 Book Appointment",
            use_container_width=True,
        ):
            navigate("📅 Appointments")

    with c:
        if st.button(
            "📋 Manage Records",
            use_container_width=True,
        ):
            navigate("📋 Medical Records")

    st.subheader("👤 Patient Profile")

    if patient:
        with st.container(border=True):
            st.write(f"**Name:** {patient['name']}")
            st.write(f"**Age:** {patient['age']}")
            st.write(f"**Patient ID:** {patient_id}")

    st.subheader("Recent Medical History")
    show_table(history[:5])

    st.subheader("Active Appointments")
    show_table(active)


# ======================================================
# PATIENT REGISTRATION
# ======================================================

elif page == "👤 Patients":

    st.header("👤 Patient Registration")

    with st.form(
        "patient_registration",
        clear_on_submit=True,
    ):
        name = st.text_input(
            "Patient Full Name",
            placeholder="Enter patient name",
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
            st.error("Enter a valid patient name.")
        else:
            try:
                new_id = create_patient(name, age)

                success_notification(
                    f"Patient {name.strip()} registered "
                    f"successfully! Patient ID: {new_id}"
                )

            except Exception as exc:
                st.error(f"Registration failed: {exc}")

    st.subheader("Registered Patients")
    show_table(as_dicts(get_patients()))


# ======================================================
# APPOINTMENT BOOKING
# ======================================================

elif page == "📅 Appointments":

    st.header("📅 Smart Appointment Booking")

    if patient_id is None:
        st.warning("Register a patient first.")
        st.stop()

    st.write(f"**Patient:** {patient['name']}")

    st.subheader("Step 1 — Patient Concern")

    concern = st.selectbox(
        "Choose Consultation Type",
        list(DEPARTMENT_GUIDE.keys()),
    )

    suggested = DEPARTMENT_GUIDE[concern]

    st.info(
        f"Suggested Department: **{suggested}**"
    )

    st.subheader("Step 2 — Medical Department")

    doctors = as_dicts(get_doctors())

    departments = sorted({
        doctor["specialization"]
        for doctor in doctors
    })

    department = st.selectbox(
        "Select Department",
        departments,
        index=(
            departments.index(suggested)
            if suggested in departments else 0
        ),
        key=f"department_{concern}",
    )

    filtered_doctors = [
        doctor for doctor in doctors
        if doctor["specialization"] == department
    ]

    st.subheader("Step 3 — Choose Doctor")

    if filtered_doctors:

        doctor_options = {
            f"{d['name']} — {d['specialization']}": d["id"]
            for d in filtered_doctors
        }

        doctor_label = st.selectbox(
            "Doctor Name",
            list(doctor_options.keys()),
        )

        doctor_id = doctor_options[doctor_label]

        doctor_data = next(
            d for d in filtered_doctors
            if d["id"] == doctor_id
        )

        with st.container(border=True):
            photo_col, info_col = st.columns([1, 2])

            with photo_col:
                st.image(
                    DOCTOR_IMAGES.get(
                        department,
                        DEFAULT_DOCTOR_IMAGE,
                    ),
                    use_container_width=True,
                )

            with info_col:
                st.subheader(doctor_data["name"])
                st.write(
                    f"**Specialization:** {department}"
                )
                st.write(
                    "**Consultation:** Appointment scheduling"
                )
                st.caption(
                    "Illustrative profile image. "
                    "Doctor and schedule are simulated."
                )

        st.subheader("Step 4 — Available Slots")

        try:
            slots = get_available_slots(
                doctor_id,
                days=7,
            )
        except Exception as exc:
            slots = []
            st.error(f"Slot retrieval failed: {exc}")

        if slots:

            slot = st.selectbox(
                "Appointment Date and Time",
                slots,
            )

            with st.container(border=True):
                st.write(
                    f"**Patient:** {patient['name']}"
                )
                st.write(
                    f"**Doctor:** {doctor_data['name']}"
                )
                st.write(
                    f"**Department:** {department}"
                )
                st.write(
                    f"**Time:** {slot}"
                )

                confirmed = st.checkbox(
                    "Confirm this appointment",
                )

                if st.button(
                    "✅ Book Appointment",
                    type="primary",
                    disabled=not confirmed,
                    use_container_width=True,
                ):
                    try:
                        result = book_appointment(
                            patient_id,
                            doctor_id,
                            slot,
                        )

                        if result_success(result):
                            success_notification(
                                "Appointment booked successfully! "
                                f"{doctor_data['name']} — {slot}"
                            )
                        else:
                            st.error(result_error(result))

                    except Exception as exc:
                        st.error(
                            f"Booking failed: {exc}"
                        )
        else:
            st.warning(
                "No available slots for this doctor."
            )

    st.divider()
    st.subheader("Appointment History")

    bookings = as_dicts(
        get_patient_appointments(patient_id)
    )

    show_table(bookings)

    active = [
        b for b in bookings
        if b.get("status") == "Booked"
    ]

    if active:

        cancel_options = {
            (
                f"#{b['id']} — "
                f"{b.get('doctor_name', 'Doctor')} — "
                f"{b['appointment_time']}"
            ): b["id"]
            for b in active
        }

        selected_cancel = st.selectbox(
            "Select Appointment to Cancel",
            list(cancel_options.keys()),
        )

        confirm_cancel = st.checkbox(
            "Confirm cancellation",
        )

        if st.button(
            "❌ Cancel Appointment",
            disabled=not confirm_cancel,
        ):
            try:
                result = cancel_appointment(
                    cancel_options[selected_cancel]
                )

                if result_success(result):
                    success_notification(
                        "Appointment cancelled successfully."
                    )
                else:
                    st.error(result_error(result))

            except Exception as exc:
                st.error(str(exc))


# ======================================================
# MEDICAL RECORDS
# ======================================================

elif page == "📋 Medical Records":

    st.header("📋 Medical Records")

    if patient_id is None:
        st.warning("Select a patient.")
        st.stop()

    st.write(f"**Patient:** {patient['name']}")

    records = as_dicts(
        get_medical_history(patient_id)
    )

    show_table(records)

    st.subheader("➕ Add Medical Record")

    with st.form("add_record", clear_on_submit=True):

        diagnosis = st.text_input(
            "Diagnosis or Condition",
        )

        treatment = st.text_area(
            "Treatment Details",
        )

        notes = st.text_area(
            "Medical Notes",
        )

        save_record = st.form_submit_button(
            "💾 Save Record",
            type="primary",
        )

    if save_record:
        if not diagnosis.strip():
            st.error("Diagnosis is required.")
        else:
            try:
                add_medical_record(
                    patient_id,
                    diagnosis.strip(),
                    treatment,
                    notes,
                )

                success_notification(
                    "Medical record saved successfully."
                )

            except Exception as exc:
                st.error(str(exc))

    if records:
        st.subheader("✏️ Update Medical Record")

        record_options = {
            f"#{r['id']} — {r['diagnosis']}": r
            for r in records
        }

        selected_record_label = st.selectbox(
            "Choose Record",
            list(record_options.keys()),
        )

        record = record_options[
            selected_record_label
        ]

        with st.form("update_record"):

            new_diagnosis = st.text_input(
                "Diagnosis",
                value=record.get("diagnosis") or "",
            )

            new_treatment = st.text_area(
                "Treatment",
                value=record.get("treatment") or "",
            )

            new_notes = st.text_area(
                "Notes",
                value=record.get("notes") or "",
            )

            update = st.form_submit_button(
                "Update Record",
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

                    success_notification(
                        "Medical record updated successfully."
                    )

                except Exception as exc:
                    st.error(str(exc))


# ======================================================
# HISTORY SUMMARY
# ======================================================

elif page == "🩺 History Summary":

    st.header("🩺 AI Medical History Summary")

    if patient_id is None:
        st.warning("Select a patient.")
        st.stop()

    records = as_dicts(
        get_medical_history(patient_id)
    )

    show_table(records)

    if st.button(
        "✨ Generate AI Summary",
        type="primary",
        disabled=not bool(records),
    ):

        with st.spinner("Generating summary..."):

            try:
                context = generate_history_context(
                    patient_id
                )

                prompt = (
                    "Summarize only the supplied patient "
                    "medical records. Include documented "
                    "conditions, treatments and notes. "
                    "Do not invent missing information, "
                    "diagnose, or prescribe.\n\n"
                    + context
                )

                summary = generate_ai_response(prompt)

                st.session_state["summary_result"] = {
                    "patient_id": patient_id,
                    "summary": summary,
                }

                st.toast(
                    "Summary generated successfully!",
                    icon="✅",
                )

            except Exception as exc:
                st.error(f"AI summary failed: {exc}")

    saved = st.session_state.get("summary_result")

    if saved and saved["patient_id"] == patient_id:
        st.subheader("Patient History Summary")
        st.write(saved["summary"])


# ======================================================
# MEDICAL RESEARCH
# ======================================================

elif page == "🔎 Medical Research":

    st.header("🔎 Medical Research")

    topic = st.text_input(
        "Search Medical Topic",
        value="chronic kidney disease",
    )

    if st.button(
        "🔍 Search Medical Information",
        type="primary",
    ):

        if not topic.strip():
            st.warning("Enter a medical topic.")
        else:
            with st.spinner(
                "Searching trusted sources..."
            ):
                try:
                    result = retrieve_medical_information(
                        topic
                    )

                    st.session_state["research_result"] = {
                        "topic": topic,
                        "data": result,
                    }

                except Exception as exc:
                    st.error(str(exc))

    saved = st.session_state.get(
        "research_result"
    )

    if saved and saved["topic"] == topic:

        sources = saved["data"].get(
            "sources", []
        )

        if not sources:
            st.warning(
                "No verified medical sources found."
            )

        for source in sources:
            with st.container(border=True):

                st.subheader(
                    source.get(
                        "title",
                        "Medical Information",
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
                        "Open Source",
                        url,
                    )


# ======================================================
# AI HEALTHCARE ASSISTANT
# ======================================================

elif page == "🤖 AI Healthcare Assistant":

    st.header("🤖 Intelligent Healthcare Assistant")

    if patient_id is None:
        st.warning("Select a patient.")
        st.stop()

    examples = {
        "Kidney Care": (
            "Summarize the patient's medical history, "
            "find nephrology appointments, and research "
            "chronic kidney disease."
        ),
        "Heart Care": (
            "Review patient history, find cardiology "
            "appointments, and research heart health."
        ),
        "General Care": (
            "Summarize patient history and find "
            "general medicine appointments."
        ),
        "Custom Request": "",
    }

    example = st.selectbox(
        "Try an Example",
        list(examples.keys()),
    )

    query = st.text_area(
        "Healthcare Request",
        value=examples[example],
        height=150,
        key=f"query_{example}",
    )

    if st.button(
        "✨ Run AI Healthcare Agent",
        type="primary",
        use_container_width=True,
    ):

        if not query.strip():
            st.warning("Enter a request.")
        else:
            with st.spinner(
                "Planning and executing healthcare tasks..."
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
                        f"Agent execution failed: {exc}"
                    )

    saved = st.session_state.get("agent_result")

    if saved and saved["patient_id"] == patient_id:

        result = saved["result"]

        st.subheader("Agent Response")
        st.write(result.get("response", ""))

        with st.expander("Planning Breakdown"):
            st.write(result.get("plan", ""))

        with st.expander("Execution Trace"):
            st.write(
                result.get("execution_trace", [])
            )

        with st.expander("Medical Sources"):
            st.write(
                result.get("medical_sources", [])
            )

    if st.button("📅 Open Appointment Booking"):
        navigate("📅 Appointments")


# ======================================================
# FAISS MEMORY
# ======================================================

elif page == "🧠 FAISS Memory":

    st.header("🧠 Semantic Patient Memory")

    if patient_id is None:
        st.warning("Select a patient.")
        st.stop()

    query = st.text_input(
        "Search Patient Memory",
        placeholder="Example: kidney history",
    )

    if st.button(
        "🔍 Search Vector Memory",
        type="primary",
    ):

        if not query.strip():
            st.warning("Enter a search query.")
        else:
            with st.spinner(
                "Searching vector memory..."
            ):
                try:
                    from healthcare.memory import (
                        retrieve_patient_memory,
                    )

                    matches = retrieve_patient_memory(
                        patient_id,
                        query,
                    )

                    if not matches:
                        st.info(
                            "No matching memory found."
                        )

                    for index, item in enumerate(
                        matches, 1
                    ):
                        with st.container(border=True):
                            st.subheader(
                                f"Memory Match {index}"
                            )

                            st.write(
                                item.get("content", "")
                            )

                            similarity = float(
                                item.get("similarity", 0)
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

elif page == "📊 Evaluation & Monitoring":

    st.header("📊 Evaluation & Monitoring")

    try:
        from healthcare.monitoring import (
            get_agent_logs,
            get_monitoring_metrics,
        )

        st.subheader("Agent Monitoring Metrics")
        st.json(get_monitoring_metrics())

        st.subheader("Execution Logs")

        show_table(
            get_agent_logs(limit=100)
        )

    except Exception as exc:
        st.warning(
            f"Monitoring unavailable: {exc}"
        )

    try:
        from healthcare.evaluation import (
            get_evaluation_metrics,
        )

        st.subheader("Evaluation Metrics")
        st.json(get_evaluation_metrics())

    except Exception as exc:
        st.warning(
            f"Evaluation unavailable: {exc}"
        )


# ======================================================
# FOOTER
# ======================================================

st.divider()

st.caption(
    "🏥 MediFlow AI | Intelligent Healthcare Management "
    "| Gemini AI • LangGraph • FAISS • Streamlit"
)
