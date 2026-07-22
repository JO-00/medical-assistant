"""
Central configuration for the medical SQL agent.
"""

import os

# ---------------------------------------------------------------------------
# Local LLM (Ollama)
# ---------------------------------------------------------------------------

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DB_DSN = os.getenv(
    "DB_DSN"
)
# ---------------------------------------------------------------------------
# CRUD workflow
# ---------------------------------------------------------------------------

# Execution retry loop (only used once a query is deemed ready: SELECT and
# UPDATE immediately, INSERT once required fields are present, DELETE both
# for its deterministic preview and for the final execution after
# confirmation).
MAX_ATTEMPTS = 5

# A DELETE preview matching more rows than this is refused outright instead
# of asking which one (per safety requirement: too many matches = abort).
MAX_DELETE_MATCHES = 1

# Required fields per table for INSERT operations. Used by the deterministic
# layer to decide whether an INSERT is missing information before it is ever
# sent to the database. id_medecin is required everywhere it exists as a
# column so the id_medecin scope check downstream has something to validate.
REQUIRED_FIELDS = {
    "patient": {"date_naissance", "nom", "prenom", "id_medecin"},
    "rdv": {"id_patient", "date_rdv", "id_medecin"},
    "note_patient": {"id_patient", "note_medecin", "id_medecin"},
    "acte_medecin": {"acte", "duree", "prix", "id_medecin"},
}

SQL_TYPES = {"SELECT", "INSERT", "UPDATE", "DELETE"}
