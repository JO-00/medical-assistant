"""
Prompt construction.

The base SYSTEM_PROMPT (schema.py) is the only place SQL-generation
rules live and is never modified. When we are NOT in a fresh request
(i.e. we're completing missing fields, or asking the LLM to correct a
query after a database/scope error), we append extra context to the
END of that same system prompt, as instructed. The user message stays
either the doctor's raw natural-language text, or a short trigger
instruction for correction turns where there's no new doctor input.
"""

from llm_db.schema import build_system_prompt


def fresh_prompt(id_medecin: int) -> str:
    return (
        build_system_prompt()
        + f"\nThe current doctor's id_medecin is {id_medecin}. "
        f"Every generated query must be scoped to this doctor using "
        f"id_medecin = {id_medecin}.\n"
    )


def missing_fields_prompt(id_medecin: int, original_sql: str, missing_fields) -> str:
    return (
        build_system_prompt()
        + f"""
--- CONTINUATION CONTEXT (not a fresh request) ---

The current doctor's id_medecin is {id_medecin}.

The doctor already started this operation. Here is the SQL generated so far:

{original_sql}

The following required fields are still missing before this query can run:
{', '.join(sorted(missing_fields))}

The doctor's next message below is meant to supply (some of) that missing
information. Combine it with the SQL above and produce ONE completed SQL
statement. If the doctor's message clearly means they want to cancel this
operation, output ABORT instead.
"""
    )


def error_correction_prompt(id_medecin: int, sql: str, problem: str) -> str:
    return (
        build_system_prompt()
        + f"""
--- CORRECTION CONTEXT (not a fresh request) ---

The current doctor's id_medecin is {id_medecin}.

You previously generated the SQL statement below:

{sql}

The database rejected it with the following error:

{problem}

Your task is ONLY to correct the SQL while preserving the original intent.

Rules:
- Output ONLY one PostgreSQL statement.
- Never explain.
- Never use markdown.
- Preserve the user's intent.
- ABORT is reserved EXCLUSIVELY for when the USER explicitly cancelled the operation.
- A database error is NEVER a reason to output ABORT.
"""
    )
