
import sqlite3
import json
import time
from healthcare.database import get_connection


def initialize_monitoring():
    """Create agent execution log table."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module TEXT NOT NULL,
                action TEXT NOT NULL,
                success INTEGER NOT NULL,
                duration_ms REAL NOT NULL,
                details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def log_agent_action(
    module, action, success,
    duration_ms=0, details=None
):
    """Record agent tool execution results."""
    initialize_monitoring()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO agent_logs
            (module, action, success, duration_ms, details)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                module,
                action,
                int(bool(success)),
                float(duration_ms),
                json.dumps(details or {}, default=str)
            )
        )
        conn.commit()


def monitor_execution(module, action, function, *args, **kwargs):
    """Execute and monitor a function."""
    start = time.perf_counter()

    try:
        result = function(*args, **kwargs)

        success = not (
            isinstance(result, dict)
            and result.get("success") is False
        )

        log_agent_action(
            module,
            action,
            success,
            (time.perf_counter() - start) * 1000
        )

        return result

    except Exception as exc:
        log_agent_action(
            module,
            action,
            False,
            (time.perf_counter() - start) * 1000,
            {"error_type": type(exc).__name__}
        )
        raise


def get_agent_logs(limit=100):
    """Return recent agent execution logs."""
    initialize_monitoring()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM agent_logs
            ORDER BY id DESC LIMIT ?
            """,
            (max(1, int(limit)),)
        ).fetchall()

    return [dict(row) for row in rows]


def get_monitoring_metrics():
    """Calculate tool execution metrics."""
    initialize_monitoring()

    with get_connection() as conn:
        row = conn.execute("""
            SELECT
                COUNT(*) AS total_calls,
                COALESCE(SUM(success), 0) AS successful_calls,
                COALESCE(AVG(duration_ms), 0) AS avg_duration_ms
            FROM agent_logs
        """).fetchone()

    total = row["total_calls"]
    successful = row["successful_calls"]

    return {
        "total_calls": total,
        "successful_calls": successful,
        "failed_calls": total - successful,
        "success_rate": (
            round(successful / total * 100, 2)
            if total else 0
        ),
        "average_duration_ms": round(
            row["avg_duration_ms"], 2
        )
    }
