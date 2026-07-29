from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional , List
from datetime import datetime
import ollama
from llm_db.entrypoint import handle_database_request , handle_conversational_request




app = FastAPI()

class ConversationHistory(BaseModel):
    doctor_id: int
    session_id: Optional[int] = None  
    content: List[tuple[str,str]]
    timestamp: Optional[datetime] = None
    dynamic_context: str = ""
    detected_language: Optional[str] = None
    intent: Optional[str] = None
    last_response : Optional[str] = ""
    domain : str = "system"
    database_mode_enabled : bool = False 



@app.post("/llm_service")
def respond(session: ConversationHistory) -> ConversationHistory:

    if session.database_mode_enabled:
        response = handle_database_request(session)
    else:
        response = handle_conversational_request(session)
        
    session.content.append(("Assistant", response))
    session.last_response = response

    return session





@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "llm_service"}



def warmup_models():
    ollama.generate(
        model="qwen2.5:1.5b",
        prompt="",
        options={
            "num_ctx": 800,
            "num_predict": 1,
            "num_gpu": 0
        },
        keep_alive="30m"
    )

    ollama.generate(
            model="qwen2.5-coder:3b",
            prompt="",
            keep_alive="30m",
            options = {"num_gpu" : 999, "temperature" : 0 , "num_predict" : 1 , "num_ctx": 2048}
        )
warmup_models()