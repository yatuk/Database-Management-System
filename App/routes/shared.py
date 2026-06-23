"""Shared query helpers used across domain route modules."""

from typing import Any, Optional

from flask import session

from App.db import get_db


def get_countries() -> list[dict[str, Any]]:
    """Return all countries as a list of dicts, ordered by name."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(
        """
        SELECT country_id, country_name, country_code, region
        FROM countries
        ORDER BY country_name
        """
    )
    rows = cur.fetchall()
    cur.close()
    return rows


def get_indicators(
    table: str,
    id_column: str,
    name_column: str,
    extra_columns: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    """Return indicators from *table* with the given column names."""
    cols = ", ".join((id_column, name_column) + extra_columns)
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(f"SELECT {cols} FROM {table} ORDER BY {name_column}")
    rows = cur.fetchall()
    cur.close()
    return rows


def build_sort_clause(
    sort_map: dict[str, str],
    default: str,
    sort_by: Optional[str] = None,
    order: Optional[str] = None,
) -> tuple[str, str]:
    """Return a safe (column, direction) pair from whitelisted *sort_map*."""
    column = sort_map.get(sort_by or "", default)
    direction = "ASC" if (order or "").upper() == "ASC" else "DESC"
    return column, direction


def log_audit(
    cur: Any,
    action_type: str,
    table_name: str,
    record_id: int,
) -> None:
    """Insert an audit log entry using the current session's student_id."""
    student_id = session.get("student_id")
    if not student_id:
        return
    cur.execute(
        """
        INSERT INTO audit_logs (student_id, action_type, table_name, record_id)
        VALUES (%s, %s, %s, %s)
        """,
        (student_id, action_type, table_name, record_id),
    )


def safe_float(value: Any) -> Optional[float]:
    """Convert *value* to float, or return None."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
