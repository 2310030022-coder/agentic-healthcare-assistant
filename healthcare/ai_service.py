
from healthcare.config import generate_ai_response

from healthcare.prompts import (
    SYSTEM_PROMPT,
    PLANNING_PROMPT,
    MEDICAL_SUMMARY_PROMPT,
    MEDICAL_SEARCH_PROMPT
)

from healthcare.records import (
    get_patient,
    generate_history_context
)


def create_agent_plan(user_query):
    """
    Use Gemini to break a patient request
    into a sequence of tasks.
    """
    if not user_query or not user_query.strip():
        return "Please enter a healthcare request."

    prompt = PLANNING_PROMPT.format(
        user_query=user_query
    )

    return generate_ai_response(
        SYSTEM_PROMPT + "\n\n" + prompt
    )


def summarize_patient_history(patient_id):
    """
    Retrieve patient records and use Gemini
    to generate a medical-history summary.
    """
    patient = get_patient(patient_id)

    if patient is None:
        return "Patient not found."

    medical_history = generate_history_context(
        patient_id
    )

    prompt = MEDICAL_SUMMARY_PROMPT.format(
        medical_history=medical_history
    )

    return generate_ai_response(
        SYSTEM_PROMPT + "\n\n" + prompt
    )


def summarize_medical_research(user_query, sources):
    """
    Summarize retrieved medical information
    using Gemini.

    Sources must be retrieved separately
    from trusted medical websites.
    """
    if not sources:
        return (
            "No verified medical sources were retrieved. "
            "Unable to generate a grounded summary."
        )

    source_text = "\n\n".join(
        (
            f"Title: {source.get('title', 'Unknown')}\n"
            f"URL: {source.get('url', 'Unavailable')}\n"
            f"Content: {source.get('content', '')}"
        )
        for source in sources
    )

    prompt = MEDICAL_SEARCH_PROMPT.format(
        user_query=user_query,
        retrieved_context=source_text
    )

    return generate_ai_response(
        SYSTEM_PROMPT + "\n\n" + prompt
    )


def ask_healthcare_assistant(
    user_query,
    patient_id=None
):
    """
    Generate a plan and optionally summarize
    the selected patient's medical history.

    This is an AI service, not yet an
    autonomous tool-executing agent.
    """
    result = {
        "request": user_query,
        "plan": create_agent_plan(user_query),
        "patient_summary": None
    }

    if patient_id is not None:
        result["patient_summary"] = (
            summarize_patient_history(patient_id)
        )

    return result
