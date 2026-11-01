
import os
from google import genai


def get_gemini_api_key():
    """Get Gemini API key from environment or Streamlit Secrets."""

    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except (ImportError, FileNotFoundError, KeyError):
        return None


def get_gemini_client():
    """Initialize Gemini AI client."""

    api_key = get_gemini_api_key()

    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. "
            "Add GEMINI_API_KEY to Streamlit Secrets."
        )

    return genai.Client(api_key=api_key)


def generate_ai_response(prompt):
    """Generate an AI response using Gemini."""

    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if not response.text:
        raise RuntimeError(
            "Gemini returned an empty response."
        )

    return response.text
