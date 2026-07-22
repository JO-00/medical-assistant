"""
Deterministic database access layer.

The LLM never talks to the database directly. Every statement passes
through here, and every result/error is reported back as plain data so
the workflow layer (sql_agent.py) can decide what to do with it.
"""

import re

import psycopg2
import psycopg2.extras

from llm_db.config import DB_DSN


def get_connection():
    return psycopg2.connect(DB_DSN)


def execute_sql(sql: str):
    """
    Execute a single SQL statement.

    Returns:
        (success: bool, payload)

        - success=True,  payload = list[dict] of rows (empty list for
          statements that return nothing, e.g. INSERT/UPDATE/DELETE
          without RETURNING)
        - success=False, payload = str error message from the database
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql)

            if cur.description is not None:
                rows = [dict(r) for r in cur.fetchall()]
            else:
                rows = []

        conn.commit()
        return True, rows

    except Exception as exc:  # noqa: BLE001 - we want to surface any DB error
        if conn is not None:
            conn.rollback()
        return False, str(exc)

    finally:
        if conn is not None:
            conn.close()


def build_delete_preview(delete_sql: str) -> str:
    """
    Turn:
        DELETE FROM patient WHERE nom ILIKE '%marilyn%' AND id_medecin = 2;
    into:
        SELECT * FROM patient WHERE nom ILIKE '%marilyn%' AND id_medecin = 2;

    This is purely mechanical (no LLM involved) so we can always safely
    preview what a DELETE would affect before running it.
    """
    preview = re.sub(
        r"^\s*DELETE\s+FROM\b",
        "SELECT * FROM",
        delete_sql.strip(),
        count=1,
        flags=re.IGNORECASE,
    )

    if preview == delete_sql.strip():
        raise ValueError(f"Could not build a preview for non-DELETE SQL: {delete_sql}")

    return preview
