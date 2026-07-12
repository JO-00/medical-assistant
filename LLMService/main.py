from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional , List
from datetime import datetime
from ollama_api import call_ollama

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
    context = build_context(session)
    print(context)
    response = call_ollama(user_message=context, system_prompt="")
    
    # Add the assistant's response to the session content
    session.content.append(('Assistant', response))
    session.last_response = response
    import logging
    logger = logging.getLogger()
    logger.critical(f"POV llm service : {session}")
    return session


@app.post("/ollama")
def respond(data : dict) -> str:
    assert "user_message" in data and "system_prompt" in data
    return call_ollama(user_message= data["user_message"] , system_prompt=data["system_prompt"])



@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm_service"}

