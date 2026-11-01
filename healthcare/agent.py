
import json
import re
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from healthcare.config import generate_ai_response
from healthcare.records import (
    get_patient,
    generate_history_context
)
from healthcare.appointments import (
    get_doctors,
    get_available_slots
)
from healthcare.ai_service import (
    summarize_patient_history,
    create_agent_plan
)


class HealthcareState(TypedDict, total=False):
    user_query: str
    patient_id: int
    plan: str
    intent: dict
    patient_context: str
    doctor_results: list
    available_slots: list
    patient_summary: str
    response: str
    execution_trace: list


def identify_intent(state: HealthcareState):
    """Use Gemini to identify requested healthcare tasks."""

    query = state["user_query"]

    prompt = f"""
    Analyze this healthcare request:

    {query}

    Return ONLY a JSON object with these boolean keys:
    - needs_history
    - needs_appointment
    - needs_medical_search

    Also include:
    - specialization: medical specialty requested,
      or an empty string if not specified.

    Do not include markdown formatting.
    """

    raw = generate_ai_response(prompt)

    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        raw.strip()
    )

    try:
        intent = json.loads(cleaned)
    except (json.JSONDecodeError, TypeError):
        intent = {
            "needs_history": False,
            "needs_appointment": False,
            "needs_medical_search": False,
            "specialization": ""
        }

    return {
        "intent": intent,
        "execution_trace": ["Intent identified"]
    }


def planning_node(state: HealthcareState):
    """Generate a task decomposition plan."""

    plan = create_agent_plan(state["user_query"])

    return {
        "plan": plan,
        "execution_trace": (
            state.get("execution_trace", [])
            + ["Task plan generated"]
        )
    }


def retrieve_history_node(state: HealthcareState):
    """Retrieve selected patient history."""

    patient_id = state.get("patient_id")

    if patient_id is None:
        context = "No patient selected."
    else:
        patient = get_patient(patient_id)

        if patient is None:
            context = "Patient not found."
        else:
            context = generate_history_context(patient_id)

    return {
        "patient_context": context,
        "execution_trace": (
            state.get("execution_trace", [])
            + ["Patient history lookup completed"]
        )
    }


def appointment_node(state: HealthcareState):
    """Search for doctors and available appointments."""

    specialty = state.get("intent", {}).get(
        "specialization", ""
    )

    doctors = get_doctors(specialty or None)

    slots = []

    for doctor in doctors:
        available = get_available_slots(
            doctor["id"], days=7
        )

        slots.append({
            "doctor": doctor,
            "available_slots": available[:5]
        })

    return {
        "doctor_results": doctors,
        "available_slots": slots,
        "execution_trace": (
            state.get("execution_trace", [])
            + ["Doctor availability checked"]
        )
    }


def history_summary_node(state: HealthcareState):
    """Summarize existing medical history with Gemini."""

    patient_id = state.get("patient_id")

    if patient_id is None:
        summary = "No patient selected."
    elif get_patient(patient_id) is None:
        summary = "Patient not found."
    else:
        summary = summarize_patient_history(patient_id)

    return {
        "patient_summary": summary,
        "execution_trace": (
            state.get("execution_trace", [])
            + ["Medical history summarized"]
        )
    }


def response_node(state: HealthcareState):
    """Prepare a response from completed tool results."""

    sections = []

    if state.get("patient_summary"):
        sections.append(
            "PATIENT HISTORY SUMMARY:\n"
            + state["patient_summary"]
        )

    if state.get("available_slots"):
        sections.append(
            "AVAILABLE DOCTOR APPOINTMENTS:\n"
            + json.dumps(
                state["available_slots"],
                indent=2
            )
        )

    if state.get("intent", {}).get(
        "needs_medical_search", False
    ):
        sections.append(
            "MEDICAL RESEARCH:\n"
            "Trusted-source retrieval is not yet "
            "connected. No medical research was performed."
        )

    if not sections:
        sections.append(
            "No executable healthcare task was identified."
        )

    return {
        "response": "\n\n".join(sections),
        "execution_trace": (
            state.get("execution_trace", [])
            + ["Final response prepared"]
        )
    }


def route_after_planning(state: HealthcareState):
    intent = state.get("intent", {})

    if intent.get("needs_history"):
        return "history"

    if intent.get("needs_appointment"):
        return "appointments"

    return "response"


def route_after_history(state: HealthcareState):
    intent = state.get("intent", {})

    if intent.get("needs_appointment"):
        return "appointments"

    return "summary"


def build_healthcare_agent():
    graph = StateGraph(HealthcareState)

    graph.add_node("identify_intent", identify_intent)
    graph.add_node("planning", planning_node)
    graph.add_node("history", retrieve_history_node)
    graph.add_node("appointments", appointment_node)
    graph.add_node("summary", history_summary_node)
    graph.add_node("response", response_node)

    graph.add_edge(START, "identify_intent")
    graph.add_edge("identify_intent", "planning")

    graph.add_conditional_edges(
        "planning",
        route_after_planning,
        {
            "history": "history",
            "appointments": "appointments",
            "response": "response"
        }
    )

    graph.add_conditional_edges(
        "history",
        route_after_history,
        {
            "appointments": "appointments",
            "summary": "summary"
        }
    )

    graph.add_edge("appointments", "summary")
    graph.add_edge("summary", "response")
    graph.add_edge("response", END)

    return graph.compile()


def run_healthcare_agent(user_query, patient_id=None):
    """Run the complete healthcare planning workflow."""

    if not user_query or not user_query.strip():
        return {
            "response": "Please enter a healthcare request.",
            "execution_trace": []
        }

    agent = build_healthcare_agent()

    initial_state = {
        "user_query": user_query,
        "execution_trace": []
    }

    if patient_id is not None:
        initial_state["patient_id"] = patient_id

    return agent.invoke(initial_state)
