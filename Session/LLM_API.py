import requests, logging
from data_structures import ConversationHistory
import os
LLM_SERVICE_URL=os.getenv("LLM_SERVICE_URL")

logger = logging.getLogger()

def call_ollama(user_message: str, system_prompt: str = None) -> str:
    response = requests.post(
        LLM_SERVICE_URL+"/ollama",
        json={
            "user_message": user_message,
            "system_prompt": system_prompt or ""
        }
    )
    return response.text  # Your LLM service returns a string

def call_inference(session: ConversationHistory) -> ConversationHistory:
    session_dict = session.model_dump(mode='json')  # ← Forces datetime to ISO string
    print(f"DEBUG: session_dict = {session_dict}")
    
    response = requests.post(
        LLM_SERVICE_URL+"/llm_service",
        json=session_dict
    )
    response.raise_for_status()
    return ConversationHistory(**response.json())


def continue_database_session(
    doctor_id: int,
    session_id: int,
    prompt: str,
):

    requests.post(
        "http://llm-service:8000/continue_db_session",
        json={
            "doctor_id": doctor_id,
            "session_id": session_id,
            "prompt": prompt,
        },
        timeout=30,
    )


