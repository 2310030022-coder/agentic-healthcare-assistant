
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

from healthcare.records import generate_history_context
from healthcare.appointments import (
    get_doctors,
    get_available_slots,
)


DEPARTMENT_KEYWORDS = {
    "Nephrology": ["kidney", "renal", "bladder", "urinary"],
    "Cardiology": ["heart", "cardiac", "palpitation"],
    "Neurology": ["brain", "headache", "migraine", "nerve"],
    "Orthopedics": ["bone", "joint", "fracture", "knee"],
    "Dermatology": ["skin", "hair", "rash", "acne"],
    "Gastroenterology": ["stomach", "digestive", "gastric"],
    "Endocrinology": ["diabetes", "thyroid", "hormone"],
    "Pulmonology": ["lung", "breathing", "asthma"],
    "Ophthalmology": ["eye", "vision"],
    "ENT": ["ear", "nose", "throat"],
    "Gynecology": ["menstrual", "pregnancy", "gynecology"],
    "Psychiatry": ["anxiety", "depression", "psychiatry"],
    "Pediatrics": ["child", "pediatric"],
}


def detect_department(query):
    query = str(query).lower()

    for department, keywords in DEPARTMENT_KEYWORDS.items():
        if any(word in query for word in keywords):
            return department

    return "General Medicine"


def google_search(query, max_results=5):
    """
    Retrieve Google Search result links.
    Google may block automated scraping, so failures
    are handled without crashing the application.
    """
    results = []

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/120.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for heading in soup.select("h3"):
            anchor = heading.find_parent("a")

            if not anchor:
                continue

            title = heading.get_text(
                " ",
                strip=True,
            )

            link = anchor.get("href", "")

            if link.startswith("/url?q="):
                link = link.split("/url?q=", 1)[1].split("&", 1)[0]

            if not link.startswith("http"):
                continue

            if "google.com" in link:
                continue

            if not any(
                item["url"] == link
                for item in results
            ):
                results.append({
                    "title": title,
                    "url": link,
                })

            if len(results) >= max_results:
                break

    except requests.RequestException:
        pass

    return results


def run_healthcare_agent(user_query, patient_id=None):

    if not str(user_query).strip():
        return {
            "response": "Please enter a healthcare request.",
            "plan": [],
            "execution_trace": [],
            "medical_sources": [],
            "doctors": [],
        }

    plan = [
        "Understand the healthcare request",
        "Retrieve patient history",
        "Identify the relevant department",
        "Find matching doctors and appointment slots",
        "Search Google for healthcare resources",
        "Present results",
    ]

    trace = []
    department = detect_department(user_query)

    # Patient history
    history = "No patient history is available."

    if patient_id is not None:
        try:
            result = generate_history_context(patient_id)

            if result:
                history = str(result)

            trace.append("Patient history retrieved")

        except Exception:
            trace.append("Patient history unavailable")

    # Doctors
    doctor_details = []

    try:
        doctors = [
            dict(doctor)
            for doctor in get_doctors()
        ]

        matched = [
            doctor
            for doctor in doctors
            if doctor.get("specialization") == department
        ]

        for doctor in matched[:5]:
            try:
                slots = list(
                    get_available_slots(
                        doctor["id"],
                        days=7,
                    )
                )
            except Exception:
                slots = []

            doctor_details.append({
                "doctor": doctor["name"],
                "department": department,
                "available_slots": slots[:5],
            })

        trace.append("Doctor availability checked")

    except Exception:
        trace.append("Doctor lookup unavailable")

    # Google Search
    sources = google_search(
        user_query + " medical information",
        max_results=5,
    )

    trace.append(
        f"Google Search returned {len(sources)} links"
    )

    lines = [
        "### Healthcare Request",
        user_query,
        "",
        "### Suggested Department",
        department,
        "",
        "### Patient History",
        history,
        "",
        "### Matching Doctors",
    ]

    if doctor_details:
        for doctor in doctor_details:
            lines.append(
                f"**{doctor['doctor']}** — "
                f"{doctor['department']}"
            )

            slots = doctor["available_slots"]

            if slots:
                lines.append(
                    "Available slots: "
                    + ", ".join(str(s) for s in slots[:3])
                )
    else:
        lines.append("No matching doctors found.")

    lines.extend([
        "",
        "### Google Search Results",
    ])

    if sources:
        for source in sources:
            lines.append(
                f"- [{source['title']}]({source['url']})"
            )
    else:
        lines.append(
            "Google results could not be retrieved. "
            "Use the Google Search link below."
        )

    google_url = (
        "https://www.google.com/search?q="
        + quote_plus(user_query + " health information")
    )

    lines.append(
        f"[Open Google Search]({google_url})"
    )

    lines.append(
        "\nSearch results are external references, "
        "not verified medical advice."
    )

    return {
        "response": "\n\n".join(lines),
        "plan": plan,
        "execution_trace": trace,
        "medical_sources": sources,
        "department": department,
        "doctors": doctor_details,
        "ai_success": False,
    }
