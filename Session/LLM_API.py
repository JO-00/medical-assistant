import requests, logging
from data_structures import ConversationHistory

logger = logging.getLogger()

def call_ollama(user_message: str, system_prompt: str = None) -> str:
    response = requests.post(
        "http://llm_service:8000/ollama",
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
        "http://llm_service:8000/llm_service",
        json=session_dict
    )
    response.raise_for_status()
    return ConversationHistory(**response.json())
    


