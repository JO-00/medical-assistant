import httpx
from config import SESSION_SERVICE_URL

async def start_new_session(doctor_id: int) -> int:
    """Hits the separate /create_session endpoint to retrieve a real session ID."""
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{SESSION_SERVICE_URL}/create_session?doctor_id={doctor_id}", timeout=10.0)
            if res.status_code == 200:
                return res.json().get("session_id")
            raise Exception("Could not initialize session")
        except Exception:
            return 1 # Fallback ID so the system doesn't crash if downstream is offline

async def forward_audio_to_session_service(doctor_id: int, session_id: int, message: str) -> str:
    """Forwards text to /session with an absolute infinite timeout."""
    payload = {
        "doctor_id": doctor_id,
        "session_id": session_id,
        "message": message
    }
    # 🚨 Setting timeout to None removes all connection, read, and write limits completely
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            res = await client.post(f"{SESSION_SERVICE_URL}/session", json=payload)
            if res.status_code == 200:
                return res.json().get("last_response") or "Je n'ai pas pu formuler de réponse."
            return "Une erreur est survenue."
        except Exception:
            return "Le service de session est injoignable."