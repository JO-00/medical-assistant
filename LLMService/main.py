from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional , List
from datetime import datetime
from ollama_api import call_ollama
from llm_db.main import router, handle_database_request

class ConversationHistory(BaseModel):
    doctor_id: int
    session_id: Optional[int] = None  
    content: List[tuple[str,str]]
    timestamp: Optional[datetime] = None
    dynamic_context: str = ""
    detected_language: Optional[str] = None
    intent: Optional[str] = None
    last_response : Optional[str] = ""


app = FastAPI()
app.include_router(router)


def build_context(session: ConversationHistory) -> str:
    context = session.dynamic_context + "\n==============\nCONVERSATION HISTORY\n==============\n"
    
    # Build history from all messages except the last one
    for speaker, text in session.content[:-1]:
        context += f"{speaker}: {text}\n"
    
    # Add the last message as the current user input
    if session.content:
        last_speaker, last_text = session.content[-1]
        context += "Maintenant réponds à cette requête : \n" if session.detected_language == "fr" else "Now Answer this user input: \n"
        context += f"\n{last_speaker} :  {last_text}"
    
    return context



@app.post("/llm_service")
def respond(session: ConversationHistory) -> ConversationHistory:

    if session.intent == "database":
        response = handle_database_request(session)

    else:
        context = build_context(session)
        response = call_ollama(
            user_message=context,
            system_prompt=""
        )

    session.content.append(("Assistant", response))
    session.last_response = response

    return session


@app.post("/ollama")
def respond(data : dict) -> str:
    assert "user_message" in data and "system_prompt" in data
    return call_ollama(user_message= data["user_message"] , system_prompt=data["system_prompt"])



@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm_service"}

