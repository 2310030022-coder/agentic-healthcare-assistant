
import os
from functools import lru_cache
from google import genai


def get_api_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()

    if not key:
        try:
            import streamlit as st
            key = str(st.secrets.get("GEMINI_API_KEY", "")).strip()
        except Exception:
            pass

    if not key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it in Streamlit Cloud > App settings > Secrets."
        )

    return key


@lru_cache(maxsize=1)
def get_client():
    return genai.Client(api_key=get_api_key())


def available_models():
    client = get_client()
    models = []

    for model in client.models.list():
        name = getattr(model, "name", "")

        if name.startswith("models/"):
            name = name[7:]

        actions = (
            getattr(model, "supported_actions", None)
            or getattr(model, "supported_generation_methods", None)
        )

        if (
            name.startswith("gemini-")
            and (not actions or "generateContent" in actions)
            and "image" not in name.lower()
            and "live" not in name.lower()
        ):
            models.append(name)

    preferred = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
    ]

    return (
        [m for m in preferred if m in models]
        + [m for m in models if m not in preferred and "flash" in m]
        + [m for m in models if m not in preferred and "flash" not in m]
    )


def generate_ai_response(prompt):
    client = get_client()

    try:
        models = available_models()
    except Exception as exc:
        raise RuntimeError(
            f"Could not access Gemini model list: {exc}"
        ) from exc

    if not models:
        raise RuntimeError(
            "No Gemini text-generation models are available "
            "for this API key."
        )

    errors = []

    for model in models[:6]:
        try:
            response = client.models.generate_content(
                model=model,
                contents=str(prompt),
            )

            answer = getattr(response, "text", None)

            if answer and answer.strip():
                return answer.strip()

            errors.append(f"{model}: Empty response")

        except Exception as exc:
            error = str(exc)
            errors.append(f"{model}: {error[:350]}")

            if any(
                text in error.lower()
                for text in (
                    "api_key_invalid",
                    "api key not valid",
                    "permission_denied",
                    "resource_exhausted",
                    "quota exceeded",
                    "429",
                )
            ):
                break

    raise RuntimeError(
        "Gemini request failed:\n" + "\n".join(errors)
    )
