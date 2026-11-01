
import os

from google import genai


def get_gemini_api_key():
    """Retrieve the Gemini API key securely."""
    api_key = os.getenv("GEMINI_API_KEY")

    if api_key:
        return api_key

    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY")
    except (ImportError, FileNotFoundError, KeyError):
        return None


def get_gemini_client():
    """Create an authenticated Gemini client."""
    api_key = get_gemini_api_key()

    if not api_key:
        raise RuntimeError(
            "Gemini API key is missing. "
            "Configure GEMINI_API_KEY in Streamlit Secrets."
        )

    return genai.Client(api_key=api_key)


def generate_ai_response(prompt):
    """Generate a response using Google Gemini."""
    client = get_gemini_client()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
