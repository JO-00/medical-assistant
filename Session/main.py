from fastapi import FastAPI
from pydantic import BaseModel
from session_management import handle_input , manager
from ContextManager import ConversationHistory
from session_management import ConversationHistories
from typing import Optional
import redis,json

app = FastAPI()


class Req (BaseModel):
    doctor_id : int
    session_id : Optional[int] = None
    message : str



@app.post("/session")
def handle_session(request : Req) -> ConversationHistory :
    return handle_input(request.model_dump())

@app.post("/create_session")
def get_new_session(doctor_id : int) -> ConversationHistory :
    return manager.create_new_session(doctor_id)


@app.get("/conversations")
def get_conversations(
    id: int,
    email: Optional[str] = None,
    name: Optional[str] = None
):
    doctor_id = id
    pattern = f"conversation:{doctor_id}:*"
    r = redis.Redis(host="redis", port=6379, decode_responses=True)
    keys = r.keys(pattern)
    
    conversations = []
    for key in keys:
        raw_session = r.get(key)
        if not raw_session:
            continue
        session = ConversationHistory(**json.loads(raw_session))
        
        session_id = int(key.split(':')[-1])
        
        conversations.append({
            "id": session_id,
            "timestamp": session.timestamp.isoformat() if session.timestamp else "unknown",  
            "content": [ 
                {
                    "sender": sender,
                    "message": message
                }
                for sender, message in session.content
            ],
            "detectedLanguage": session.detected_language  
        })
    
    # Sort by session ID (newest first)
    conversations.sort(key=lambda x: x["id"], reverse=True)
    
    return conversations




