
import os
import re
import time
import random
from functools import lru_cache

from google import genai


def get_api_key():
    key = os.getenv("GEMINI_API_KEY", "").strip()

    if not key:
        try:
            import streamlit as st
            key = str(
                st.secrets.get("GEMINI_API_KEY", "")
            ).strip()
        except Exception:
            pass

    if not key:
        raise RuntimeError(
            "Gemini API key is missing. "
            "Add GEMINI_API_KEY in Streamlit Cloud Secrets."
        )

    return key


@lru_cache(maxsize=1)
def get_client():
    return genai.Client(api_key=get_api_key())


def get_available_models():
    client = get_client()
    names = []

    try:
        for model in client.models.list():
            name = str(
                getattr(model, "name", "")
            ).removeprefix("models/")

            actions = (
                getattr(model, "supported_actions", None)
                or getattr(
                    model,
                    "supported_generation_methods",
                    None,
                )
            )

            if not name.startswith("gemini-"):
                continue

            if any(
                excluded in name.lower()
                for excluded in (
                    "embedding",
                    "image",
                    "live",
                    "tts",
                    "audio",
                    "robotics",
                )
            ):
                continue

            if actions and "generateContent" not in actions:
                continue

            names.append(name)

    except Exception as exc:
        raise RuntimeError(
            "Unable to retrieve available Gemini models. "
            f"Details: {str(exc)[:200]}"
        ) from exc

    preferred = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ]

    ordered = [
        model
        for model in preferred
        if model in names
    ]

    ordered.extend(
        model
        for model in names
        if model not in ordered
        and "flash" in model.lower()
    )

    ordered.extend(
        model
        for model in names
        if model not in ordered
    )

    return list(dict.fromkeys(ordered))


def get_error_code(exc):
    for field in ("code", "status_code"):
        value = getattr(exc, field, None)

        try:
            return int(value)
        except (TypeError, ValueError):
            pass

    match = re.search(
        r"\b(400|401|403|404|429|500|502|503|504)\b",
        str(exc),
    )

    return int(match.group(1)) if match else None


def generate_ai_response(prompt):
    if not str(prompt).strip():
        raise ValueError("Please enter a request.")

    client = get_client()
    models = get_available_models()

    if not models:
        raise RuntimeError(
            "No compatible Gemini text models "
            "are available for this API key."
        )

    exhausted = []
    unavailable = []
    temporary = []

    # Limit the number of models tried per request.
    for model_name in models[:8]:

        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=str(prompt),
                )

                answer = getattr(
                    response,
                    "text",
                    None,
                )

                if answer and answer.strip():
                    return answer.strip()

                unavailable.append(model_name)
                break

            except Exception as exc:
                code = get_error_code(exc)
                message = str(exc).lower()

                # Daily or rate quota reached.
                # Do not retry the same model.
                if (
                    code == 429
                    or "resource_exhausted" in message
                    or "quota exceeded" in message
                ):
                    exhausted.append(model_name)
                    break

                # Model not supported by the key.
                if code == 404:
                    unavailable.append(model_name)
                    break

                # Temporary server overload.
                if code in (500, 502, 503, 504):
                    if attempt == 0:
                        time.sleep(
                            1.0 + random.uniform(0, 0.5)
                        )
                        continue

                    temporary.append(model_name)
                    break

                # Authentication and permissions.
                if code in (400, 401, 403):
                    raise RuntimeError(
                        "Gemini API key, permissions, or "
                        "request configuration error. "
                        f"Details: {str(exc)[:250]}"
                    ) from exc

                raise RuntimeError(
                    "Gemini request failed. "
                    f"Details: {str(exc)[:250]}"
                ) from exc

    if exhausted:
        raise RuntimeError(
            "Gemini API request quota has been reached "
            "for the available models. "
            "Please wait for the quota to reset "
            "or check billing and usage in Google AI Studio. "
            "Exhausted models: "
            + ", ".join(exhausted[:5])
        )

    if temporary:
        raise RuntimeError(
            "Gemini is temporarily overloaded. "
            "Please try again later."
        )

    raise RuntimeError(
        "No compatible Gemini model returned a response. "
        "Check the models and API permissions "
        "in Google AI Studio."
    )
