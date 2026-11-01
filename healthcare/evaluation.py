
import re
from healthcare.database import get_connection


def initialize_evaluation():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                response TEXT NOT NULL,
                reference TEXT,
                relevance_score REAL,
                accuracy_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def tokenize(text):
    return set(
        re.findall(r"\b[a-z0-9]+\b", (text or "").lower())
    )


def calculate_overlap(text_a, text_b):
    """Simple lexical overlap metric."""
    a = tokenize(text_a)
    b = tokenize(text_b)

    if not a or not b:
        return 0.0

    return round(
        len(a.intersection(b)) / len(a.union(b)),
        4
    )


def evaluate_response(question, response, reference=""):
    """
    Calculate preliminary automatic metrics.

    These are lexical similarity proxies,
    not validated clinical accuracy measures.
    """
    relevance = calculate_overlap(
        question, response
    )

    accuracy = (
        calculate_overlap(response, reference)
        if reference else None
    )

    initialize_evaluation()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO evaluations
            (question, response, reference,
             relevance_score, accuracy_score)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                question,
                response,
                reference,
                relevance,
                accuracy
            )
        )
        conn.commit()

    return {
        "relevance_score": relevance,
        "reference_similarity_score": accuracy,
        "method": "Jaccard lexical overlap",
        "note": (
            "Scores do not establish medical "
            "correctness or factual accuracy."
        )
    }


def get_evaluation_metrics():
    initialize_evaluation()

    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) AS total_evaluations,
                AVG(relevance_score) AS avg_relevance,
                AVG(accuracy_score) AS avg_accuracy
            FROM evaluations
        """).fetchone()

    return {
        "total_evaluations": row["total_evaluations"],
        "average_relevance": round(
            row["avg_relevance"] or 0, 4
        ),
        "average_reference_similarity": round(
            row["avg_accuracy"] or 0, 4
        )
    }
