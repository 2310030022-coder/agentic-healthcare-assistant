
import os
import random
import time
from functools import lru_cache

from google import genai


@lru_cache(maxsize=1)
def get_client():
    key = os.environ.get("GEMINI_API_KEY", "").strip()

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
            "GEMINI_API_KEY is missing. "
            "Add it to Streamlit Cloud > Settings > Secrets."
        )

    return genai.Client(api_key=key)


def _model_names():
    client = get_client()
    names = []

    try:
        for item in client.models.list():
            name = str(getattr(item, "name", ""))
            name = name.removeprefix("models/")

            actions = getattr(
                item, "supported_actions", None
            )

            if not name.startswith("gemini-"):
                continue

            if any(
                x in name.lower()
                for x in (
                    "image", "live", "tts", "embedding"
                )
            ):
                continue

            if actions and "generateContent" not in actions:
                continue

            names.append(name)

    except Exception:
        names = [
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
        ]

    preferred = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
    ]

    ordered = [
        n for n in preferred if n in names
    ]

    ordered.extend(
        n for n in names
        if n not in ordered
        and "flash" in n.lower()
    )

    ordered.extend(
        n for n in names if n not in ordered
    )

    return ordered[:5]


def _status(exc):
    code = (
        getattr(exc, "code", None)
        or getattr(exc, "status_code", None)
    )

    try:
        return int(code)
    except (TypeError, ValueError):
        return None


def _is_temporary(exc):
    message = str(exc).lower()

    return (
        _status(exc) in (500, 502, 503, 504)
        or any(
            phrase in message
            for phrase in (
                "503",
                "unavailable",
                "high demand",
                "overloaded",
                "internal error",
                "deadline exceeded",
            )
        )
    )


def generate_ai_response(prompt):
    if not str(prompt).strip():
        raise ValueError(
            "AI prompt cannot be empty."
        )

    client = get_client()
    models = _model_names()

    if not models:
        raise RuntimeError(
            "No compatible Gemini text models "
            "are available for this API key."
        )

    failures = []

    for model in models:
        for attempt in range(3):
            try:
                response = (
                    client.models.generate_content(
                        model=model,
                        contents=str(prompt),
                    )
                )

                answer = getattr(
                    response, "text", None
                )

                if answer and answer.strip():
                    return answer.strip()

                failures.append(
                    f"{model}: empty response"
                )
                break

            except Exception as exc:
                message = str(exc)

                if _is_temporary(exc):
                    if attempt < 2:
                        time.sleep(
                            min(
                                2 ** attempt
                                + random.uniform(0, 0.5),
                                4,
                            )
                        )
                        continue

                    failures.append(
                        f"{model}: temporarily unavailable (503)"
                    )
                    break

                if (
                    _status(exc) == 404
                    or "not found" in message.lower()
                ):
                    failures.append(
                        f"{model}: not available to this API key"
                    )
                    break

                if (
                    _status(exc) == 429
                    or "resource_exhausted" in message.lower()
                    or "quota exceeded" in message.lower()
                ):
                    raise RuntimeError(
                        "Gemini API quota/rate limit reached "
                        "(429). Check Google AI Studio usage "
                        "and try later."
                    ) from exc

                if (
                    _status(exc) in (400, 401, 403)
                    or any(
                        term in message.lower()
                        for term in (
                            "api_key_invalid",
                            "api key not valid",
                            "permission_denied",
                        )
                    )
                ):
                    raise RuntimeError(
                        "Gemini API authentication or "
                        f"request error: {message[:400]}"
                    ) from exc

                failures.append(
                    f"{model}: {message[:200]}"
                )
                break

    raise RuntimeError(
        "Gemini models are currently unavailable "
        "after automatic retries and fallback. "
        "Please try again shortly. Details: "
        + " | ".join(failures[:5])
    )
