"""
Deterministic, regex-based helpers for inspecting SQL text.

Nothing here calls the LLM or the database. This is pure Python logic
used to decide workflow (SQL type/table detection, missing INSERT
fields, and the id_medecin ownership check that keeps one doctor from
ever touching another doctor's data).
"""

import re

from llm_db.config import REQUIRED_FIELDS, SQL_TYPES
import logging
logger = logging.getLogger()


def detect_sql_type(sql: str) -> str:
    first_word = sql.strip().split(None, 1)[0].upper()
    
    if first_word not in SQL_TYPES:
        logger.debug(sql)
        raise ValueError(f"Unrecognized or unsupported SQL type: {first_word!r}")

    return first_word

def detect_table(sql: str, sql_type: str) -> str:
    sql_lower = sql.lower()
    
    # For SELECT queries, determine the subject based on what's being selected
    if sql_type == "SELECT":
        # If we're selecting rdv columns, it's a rdv query
        if 'rdv.date_rdv' in sql_lower or 'r.date_rdv' in sql_lower or 'date_rdv' in sql_lower:
            return 'rdv'
        # If we're selecting patient notes
        elif 'note_patient' in sql_lower:
            return 'note_patient'
        # If we're selecting medical acts
        elif 'acte_medecin' in sql_lower:
            return 'acte_medecin'
        # If we're selecting patient info only (no rdv columns)
        elif 'patient' in sql_lower and 'rdv' not in sql_lower:
            return 'patient'
        # Fallback to the first table in FROM
        else:
            match = re.search(r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE)
            if match:
                return match.group(1).lower()
            else:
                raise ValueError(f"Could not detect target table in SQL: {sql}")
    
    # For INSERT, UPDATE, DELETE - look at the target table
    elif sql_type == "INSERT":
        match = re.search(r"INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE)
    elif sql_type == "UPDATE":
        match = re.search(r"UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE)
    elif sql_type == "DELETE":
        match = re.search(r"DELETE\s+FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, flags=re.IGNORECASE)
    else:
        raise ValueError(f"Unknown SQL type: {sql_type}")
    
    if not match:
        return None
    
    return match.group(1).lower()


# ---------------------------------------------------------------------------
# INSERT parsing
# ---------------------------------------------------------------------------

def _split_top_level(s: str):
    """Split on commas, but not commas inside single-quoted string values."""
    parts = []
    current = ""
    in_quotes = False

    for ch in s:
        if ch == "'":
            in_quotes = not in_quotes
            current += ch
        elif ch == "," and not in_quotes:
            parts.append(current.strip())
            current = ""
        else:
            current += ch

    if current.strip():
        parts.append(current.strip())

    return parts


def parse_insert(sql: str):
    """
    Given: INSERT INTO patient(nom, prenom) VALUES ('kelly', 'x');
    Return: ("patient", ["nom", "prenom"], ["'kelly'", "'x'"])

    Returns (None, [], []) if the statement doesn't match the expected
    INSERT INTO table(cols...) VALUES(vals...) shape.
    """
    match = re.search(
        r"INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)\s*VALUES\s*\(([^)]*)\)",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None, [], []

    table = match.group(1).lower()
    columns = [c.strip().strip('"').lower() for c in _split_top_level(match.group(2))]
    values = [v.strip() for v in _split_top_level(match.group(3))]

    return table, columns, values


def extract_insert_columns(sql: str) -> set:
    _table, columns, _values = parse_insert(sql)
    return {c for c in columns if c}


def missing_fields_for_insert(sql: str):
    """
    Returns (table, missing_fields_set) for an INSERT statement, purely
    deterministically, based on the REQUIRED_FIELDS config. No LLM call.
    """
    table, columns, _values = parse_insert(sql)
    if table is None:
        table = detect_table(sql, "INSERT")

    required = REQUIRED_FIELDS.get(table, set())
    present = {c for c in columns if c}
    missing = required - present

    return table, missing


# ---------------------------------------------------------------------------
# id_medecin ownership scope check
# ---------------------------------------------------------------------------

def check_id_medecin_scope(sql: str, sql_type: str, id_medecin: int):
    """
    Deterministic guard: a query must always be scoped to the current
    doctor. Returns None if the query is fine, or a plain-English
    description of the problem (to feed back to the LLM as if it were a
    database error) if it is not. Never touches the database.
    """
    if sql_type == "INSERT":
        return _check_insert_scope(sql, id_medecin)

    # SELECT / UPDATE / DELETE (and DELETE's SELECT-shaped preview) all
    # rely on a WHERE-clause filter.
    matches = re.findall(r"id_medecin\s*=\s*(\d+)", sql, flags=re.IGNORECASE)

    if not matches:
        return (
            f"This query does not filter by id_medecin at all. Every query must "
            f"restrict results to the current doctor by including "
            f"id_medecin = {id_medecin} in the WHERE clause (add it with AND if "
            f"a WHERE clause already exists)."
        )

    for value in matches:
        if int(value) != id_medecin:
            return (
                f"This query filters by id_medecin = {value}, which is not the "
                f"current doctor. It must use id_medecin = {id_medecin} exactly. "
                f"Never use a different doctor's id."
            )

    return None


def _check_insert_scope(sql: str, id_medecin: int):
    table, columns, values = parse_insert(sql)

    if table is None or "id_medecin" not in columns:
        # Either unparsable (will surface as a DB error instead) or
        # id_medecin isn't part of this INSERT yet -- that case is caught
        # earlier by missing_fields_for_insert, not here.
        return None

    idx = columns.index("id_medecin")
    raw_value = values[idx].strip().strip("'").strip('"')

    if raw_value != str(id_medecin):
        return (
            f"This INSERT sets id_medecin = {raw_value}, which is not the current "
            f"doctor. It must insert id_medecin = {id_medecin} exactly."
        )

    return None
