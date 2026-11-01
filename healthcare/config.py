
import os
from google import genai


# Gemini model recommended by the API error
GEMINI_MODEL = "gemini-3.8-flash"


def get_gemini_api_key():
    """Read Gemini API key securely."""

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")

    except (ImportError, FileNotFoundError, KeyError):
        return None


def get_gemini_client():
    """Create Gemini API client."""

    api_key = get_gemini_api_key()

    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. "
            "Please add GEMINI_API_KEY "
            "to Streamlit Secrets."
        )

    return genai.Client(api_key=api_key)


def generate_ai_response(prompt):
    """Generate a response using Gemini AI."""

    client = get_gemini_client()

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )

        if not response.text:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        return response.text

    except Exception as exc:
        raise RuntimeError(
            f"Gemini AI request failed: {exc}"
        ) from exc
