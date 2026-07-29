"""
Central configuration for the medical SQL agent.
"""

import os


OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://host.docker.internal:11434")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DB_DSN = os.getenv(
    "DB_DSN"
)
REQUIRED_FIELDS = {
    "patient": {"date_naissance", "nom", "prenom"},
    "rdv": {"id_patient", "date_rdv", "id_medecin" , "motif"},
    "note_patient": {"id_patient", "note_medecin", "id_medecin"},
    "acte_medecin": {"acte", "duree", "prix", "id_medecin"},
}

SQL_TYPES = {"SELECT", "INSERT", "UPDATE", "DELETE"}
