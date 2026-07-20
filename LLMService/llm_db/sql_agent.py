from llm_db.config import MAX_ATTEMPTS, MAX_DELETE_MATCHES
from llm_db. db import execute_sql, build_delete_preview
from llm_db.session import DatabaseSession, SessionManager
from llm_db.sql_utils import (
    detect_sql_type,
    detect_table,
    missing_fields_for_insert,
    check_id_medecin_scope,
)
from llm_db.format_service import _format_rows
from llm_db.llm_client import ask_llm
import llm_db.prompts as prompts
import re, logging
logger = logging.getLogger()

"""
Deterministic workflow layer.

The local LLM (qwen2.5:3b via Ollama) only ever translates language <->
SQL for one narrow sub-task at a time. Every decision about *what to do
next* is made here, in plain Python:

- INSERT: missing required fields are detected deterministically, no
  LLM call, before we ever consider running anything.
- DELETE: always previewed first (DELETE -> SELECT, mechanically, no
  LLM). Zero matches -> nothing to do. Exactly one match ->
  WAITING_CONFIRMATION, resolved deterministically by the doctor typing
  YES/NO (no LLM involved in reading that answer). More than one match
  -> refused outright for safety, no clarification round.
- SELECT and UPDATE go straight into the retry-with-correction loop,
  since there's nothing to deterministically check beforehand besides
  doctor ownership.
- Every query that is about to touch the database -- SELECT, UPDATE,
  INSERT (once complete), the DELETE preview, and the final DELETE --
  passes through execute_with_correction, which on every attempt first
  checks that the query is scoped to id_medecin for the current doctor
  (without ever hitting the database if it isn't), then executes it,
  feeding any database error straight back to the LLM for a correction
  attempt. This loop only ever fires for queries we're already certain
  should run.
"""





# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def sql_agent(user_query: str, session: DatabaseSession, session_manager: SessionManager):
    if session.status != "FRESH":
        return continue_session(user_query, session, session_manager)

    return start_new_operation(user_query, session, session_manager)


def start_new_operation(user_query, session, session_manager):
    system_prompt = prompts.fresh_prompt(session.id_medecin)
    logger.debug(f"start new operation\nask llm: {system_prompt}\n\n")
    sql = ask_llm(system_prompt, user_query)
    print(f"sql = {sql}")
    if sql.strip().upper() == "ABORT":
        session_manager.delete_session(session.id_medecin , session.id_session)
        return "Okay, nothing was done."

    session.query_type = detect_sql_type(sql)
    session.table = detect_table(sql, session.query_type)
    session.generated_sql = sql
    session_manager.save_session(session)

    return execute_crud(session, session_manager)


# ---------------------------------------------------------------------------
# CRUD dispatch
# ---------------------------------------------------------------------------

def execute_crud(session, session_manager):
    handlers = {
        "SELECT": handle_select,
        "INSERT": handle_insert,
        "UPDATE": handle_update,
        "DELETE": handle_delete,
    }

    handler = handlers.get(session.query_type)
    if handler is None:
        raise ValueError(f"Unsupported query_type: {session.query_type}")

    return handler(session, session_manager)


# ---------------------------------------------------------------------------
# execute_with_correction: the ONLY retry loop in the system
# ---------------------------------------------------------------------------

def execute_with_correction(sql, sql_type, session, session_manager):
    """
    Runs SQL with correction retries.

    Foreign key constraint errors are handled deterministically:
    they are reported to the user and the operation is aborted.
    They are never sent to the LLM for correction.
    """
    def is_foreign_key_error(error):
        return "violates foreign key constraint" in str(error)


    def format_foreign_key_error(error):

        match = re.search(
            r'from table "([^"]+)"',
            str(error)
        )

        if match:
            table = match.group(1)
            return (
                "Suppression annulée.\n"
                f"Cette entrée ne peut pas être supprimée "
                f"car elle a plusieurs autres entrées dans la table '{table}'. "
                "Il faut les supprimer d'abord"
            )

        return (
            "Suppression annulée.\n"
            "Cette entrée ne peut pas être supprimée car d'autres enregistrements en dépendent"
        )
    current_sql = sql
    last_payload = None

    for _attempt in range(MAX_ATTEMPTS):

        scope_error = check_id_medecin_scope(
            current_sql,
            sql_type,
            session.id_medecin
        )

        if scope_error:
            corrected = _request_correction(
                session,
                current_sql,
                scope_error
            )

            if corrected is None:
                return False, "ABORTED", current_sql

            current_sql = corrected
            continue


        success, payload = execute_sql(current_sql)

        if success:
            return True, payload, current_sql


        last_payload = payload
        logger.critical(f"payload = {payload}\nsql_type = {sql_type}\n")

        if sql_type == "DELETE" and is_foreign_key_error(payload):
            session_manager.delete_session(
                session.id_medecin, session.id_session
            )

            return (
                False,
                format_foreign_key_error(payload),
                current_sql
            )


        corrected = _request_correction(
            session,
            current_sql,
            f"Database error: {payload}"
        )

        if corrected is None:
            return False, "ABORTED", current_sql

        current_sql = corrected


    return False, last_payload, current_sql




def _request_correction(session, sql, problem):
    print("=== CORRECTION PROMPT ===")
    print(problem)

    system_prompt = prompts.error_correction_prompt(
        session.id_medecin,
        sql,
        problem
    )

    corrected = ask_llm(system_prompt, "Provide the corrected SQL now.")

    print("=== LLM SAID ===")
    print(corrected)

    if corrected.strip().upper() == "ABORT":
        return None

    return corrected


# ---------------------------------------------------------------------------
# SELECT
# ---------------------------------------------------------------------------

def handle_select(session, session_manager):
    success, payload, final_sql = execute_with_correction(
        session.generated_sql, "SELECT", session, session_manager
    )
    session.generated_sql = final_sql
    logger.debug(f"generated_sql = {final_sql}")
    session_manager.delete_session(session.id_medecin, session.id_session)

    if success:
        formatted = _format_rows(payload,session.table)
        logger.info(f"rows returned = {formatted}")
        return formatted

    if payload == "ABORTED":
        return "D'accord, l'opération a été annulée."

    return f"Je n'ai pas pu terminer cette requête après plusieurs tentatives. Dernière erreur : {payload}"

# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def handle_update(session, session_manager):
    success, payload, final_sql = execute_with_correction(
        session.generated_sql, "UPDATE", session, session_manager
    )
    session.generated_sql = final_sql
    session_manager.delete_session(session.id_medecin, session.id_session)

    if success:
        return "Record updated successfully."

    if payload == "ABORTED":
        return "Okay, the operation was cancelled."

    return f"I couldn't complete this update after several attempts. Last error: {payload}"


# ---------------------------------------------------------------------------
# INSERT
# ---------------------------------------------------------------------------

def handle_insert(session, session_manager):
    table, missing = missing_fields_for_insert(session.generated_sql)
    session.table = table

    if missing:
        session.missing_fields = missing
        session.last_clarification_question = (
            f"I still need the following information to add this {table} record: "
            + ", ".join(sorted(missing))
            + ". Could you provide it?"
        )
        session.set_status("WAITING_MISSING_FIELDS")
        session_manager.save_session(session)
        return session.last_clarification_question

    session.missing_fields = None

    success, payload, final_sql = execute_with_correction(
        session.generated_sql, "INSERT", session, session_manager
    )
    session.generated_sql = final_sql
    session_manager.delete_session(session.id_medecin, session.id_session)

    if success:
        return "Record added successfully."

    if payload == "ABORTED":
        return "Okay, the operation was cancelled."

    return f"I couldn't complete this insertion after several attempts. Last error: {payload}"


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def handle_delete(session, session_manager):
    preview_sql = build_delete_preview(session.generated_sql)

    success, payload, final_preview_sql = execute_with_correction(
        preview_sql, "SELECT", session, session_manager
    )

    if not success:
        session_manager.delete_session(session.id_medecin, session.id_session)
        if payload == "ABORTED":
            return "Okay, the operation was cancelled."
        return f"I couldn't preview this deletion. Last error: {payload}"

    rows = payload

    # Keep the DELETE in sync with whatever corrections were applied to
    # the preview (e.g. an id_medecin fix).
    corrected_delete_sql = re.sub(
        r"^\s*SELECT\s+\*\s+FROM\b",
        "DELETE FROM",
        final_preview_sql.strip(),
        count=1,
        flags=re.IGNORECASE,
    )
    session.generated_sql = corrected_delete_sql
    print(corrected_delete_sql)
    
    if len(rows) == 0:
        session_manager.delete_session(session.id_medecin, session.id_session)
        return "Je n'ai rien trouvé à supprimer dans la base de données selon votre description"

    if len(rows) > MAX_DELETE_MATCHES:
        session_manager.delete_session(session.id_medecin, session.id_session)
        # Show the entries that were found but can't be deleted all at once
        formatted_rows = _format_rows(rows[:5], session.table)
        has_more = len(rows) > 5
        response = (
            f"Je ne peux pas supprimer plusieurs entrées à la fois. "
            f"Veuillez choisir une des entrées suivantes :\n"
            f"{formatted_rows}"
        )
        if has_more:
            response += " et il existe encore d'autres éléments."
        return response

    # Exactly one match.
    session.preview_result = rows
    session.set_status("WAITING_CONFIRMATION")
    session_manager.save_session(session)
    return (
        "Vous allez supprimer:\n"
        f"{_format_rows(rows, session.table)}\n\n"
        'Pour confirmer cette suppression, dites oui ou non'
    )

# ---------------------------------------------------------------------------
# Continuation of an in-progress session
# ---------------------------------------------------------------------------

def continue_session(user_query, session, session_manager):
    if session.status == "WAITING_MISSING_FIELDS":
        return _continue_missing_fields(user_query, session, session_manager)

    if session.status == "WAITING_CONFIRMATION":
        return _continue_confirmation(user_query, session, session_manager)

    raise ValueError(f"Unexpected session status in continue_session: {session.status}")


def _continue_missing_fields(user_query, session, session_manager):
    system_prompt = prompts.missing_fields_prompt(
        session.id_medecin, session.generated_sql, session.missing_fields or set()
    )
    sql = ask_llm(system_prompt, user_query)

    if sql.strip().upper() == "ABORT":
        session_manager.delete_session(session.id_medecin, session.id_session)
        return "Okay, the operation was cancelled."

    session.generated_sql = sql
    session.query_type = detect_sql_type(sql)
    session.table = detect_table(sql, session.query_type)
    session.set_status("FRESH")  # re-evaluate from scratch: might still be missing fields
    session_manager.save_session(session)

    return execute_crud(session, session_manager)


def _continue_confirmation(user_query, session, session_manager):
    """
    Deterministic YES/NO parsing -- no LLM involved in reading the
    doctor's confirmation, since the exact wording ("YES"/"NO") was
    dictated to them explicitly.
    """
    answer = user_query.strip().lower()

    words = set(re.findall(r"\b\w+\b", answer))

    if "yes" in words or "oui" in words:
        success, payload, final_sql = execute_with_correction(
            session.generated_sql, "DELETE", session, session_manager
        )
        session.generated_sql = final_sql
        session_manager.delete_session(session.id_medecin, session.id_session)
        print(success,payload,final_sql)
        if success:
            return "Suppression réussite."
        if payload == "ABORTED":
            return "Suppression avortée."
        return f"Je n'ai pas pu supprimer cette entrée après plusieurs tentatives. L'erreur obtenue: {payload}"

    if "non" in words:
        session_manager.delete_session(session.id_medecin, session.id_session)
        return "Okay, the deletion was cancelled."

    return 'Please reply "YES" to confirm the deletion, or "NO" to cancel.'

