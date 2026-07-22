# Medical SQL Agent (local LLM: qwen2.5:3b via Ollama)

An LLM-assisted, but Python-controlled, natural-language-to-PostgreSQL
backend. The local model only ever translates language into SQL for one
narrow sub-task at a time; every workflow decision (missing fields,
confirmations, DELETE previews, doctor-ownership checks, retries, abort)
is deterministic Python.

## Files

| File | Responsibility |
|---|---|
| `session.py` | `DatabaseSession` (one in-flight operation per doctor) and `SessionManager`. |
| `sql_agent.py` | The workflow engine: `sql_agent`, `continue_session`, `execute_crud`, the four CRUD handlers, and `execute_with_correction`. |
| `sql_utils.py` | Pure regex/string helpers: SQL type/table detection, INSERT parsing, missing-field detection, and `check_id_medecin_scope` (the doctor-ownership guard). No LLM, no DB. |
| `db.py` | Executes SQL against PostgreSQL and builds `DELETE -> SELECT *` previews. |
| `llm_client.py` | Calls a local Ollama server (`qwen2.5:3b` by default) and cleans up the raw text response. |
| `prompts.py` | Appends continuation/correction context to the end of the base `SYSTEM_PROMPT` when we're not in a fresh request. |
| `schema.py` | The exact `SCHEMA` / `SYSTEM_PROMPT` you provided (date-aware, rebuilt per call). |
| `config.py` | Ollama host/model, DB DSN, `REQUIRED_FIELDS`, `MAX_ATTEMPTS`, `MAX_DELETE_MATCHES`. |
| `main.py` | CLI loop. |

## The one retry loop: `execute_with_correction`

Every query that's about to touch the database — a SELECT, an UPDATE, a
completed INSERT, a DELETE preview, or the final DELETE — goes through
`execute_with_correction(sql, sql_type, session, session_manager)`. On
each of up to `MAX_ATTEMPTS` iterations it:

1. **Checks doctor ownership first, deterministically, before ever
   touching the database.** `check_id_medecin_scope` inspects the SQL
   text for `id_medecin = <value>`. No filter at all, or the wrong
   doctor's id, and the query is never executed — instead the problem is
   sent back to the LLM as a correction task, exactly like a database
   error would be. For INSERT it checks the actual value being inserted
   instead of a WHERE clause.
2. Otherwise, executes the SQL. Success returns immediately. A real
   database error gets fed back to the LLM for a correction attempt.

This loop is only ever entered once we're already certain the operation
should run:

- **SELECT / UPDATE** → straight into `execute_with_correction`, nothing
  to check beforehand.
- **INSERT** → `missing_fields_for_insert` runs first, purely
  deterministically (no LLM call) against `REQUIRED_FIELDS` in
  `config.py`. Missing fields → `WAITING_MISSING_FIELDS`, no execution.
  Only once everything required is present does it enter the loop.
- **DELETE** → the SQL is never executed directly. `build_delete_preview`
  mechanically swaps `DELETE FROM` for `SELECT * FROM` (no LLM), and
  *that* preview goes through `execute_with_correction` (so ownership
  and DB-error correction both apply to it too). Then:
  - 0 rows → "nothing found", session closed.
  - 1 row → `WAITING_CONFIRMATION`; the doctor must reply exactly
    `"YES"` or `"NO"` — read deterministically, no LLM involved in
    interpreting the answer.
  - more than `MAX_DELETE_MATCHES` (1 by default) → refused outright for
    safety, session closed, no clarification round.
  - Only after `"YES"` is the real `DELETE` (kept in sync with whatever
    corrections were applied to the preview) sent through
    `execute_with_correction` again.

Saying **ABORT** (interpreted by the LLM) during a missing-fields or
correction turn, or replying **"NO"** during confirmation, deletes the
session immediately via `SessionManager.delete_session`.

## Setup

```bash
pip install -r requirements.txt

# make sure Ollama is running locally with the model pulled:
ollama pull qwen2.5:3b
ollama serve   # if not already running

export DATABASE_URL=postgresql://user:password@localhost:5432/medical_db
# optional overrides:
export OLLAMA_HOST=http://localhost:11434
export OLLAMA_MODEL=qwen2.5:3b

python main.py
```

## Notes / things you'll likely want to adjust

- `MAX_DELETE_MATCHES` in `config.py` controls the "too many to delete
  safely" threshold (currently 1: anything beyond exactly one match is
  refused rather than asking which row).
- `REQUIRED_FIELDS` in `config.py` is where you add/edit per-table
  required INSERT columns.
- qwen2.5:3b is small; if you see it drifting from the "return ONLY SQL"
  rule under load, `llm_client._clean` already strips common formatting
  mistakes (code fences, wrapping quotes), but you may want to tighten
  `options` (e.g. lower `temperature` further, or add `"num_predict"`)
  in `llm_client.py` if you see truncated statements.
