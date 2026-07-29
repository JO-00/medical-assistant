from fastapi import FastAPI
from pydantic import BaseModel
from session_management import handle_input , manager
from ContextManager import ConversationHistory
from typing import Optional
import redis,json
from fastapi import Depends, HTTPException
import redis


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



class SetDatabaseDomainRequest(BaseModel):
    session_id: int
    doctor_id : int
    domain: str

class ToggleDatabaseRequest(BaseModel):
    doctor_id : int
    session_id: int
    enabled: bool

r = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )


@app.post("/toggle_database")
def toggle_database(request: ToggleDatabaseRequest):
    doctor_id = request.doctor_id
    
    session = manager.load_session_context(doctor_id, request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.database_mode_enabled = request.enabled
    manager.save_session(session)
    
    # Delete DatabaseSession from Redis if disabling
    if not request.enabled:
        key = f"db:{doctor_id}:{request.session_id}"
        r.delete(key)
    
    return {"status": "ok", "enabled": request.enabled}


@app.post("/set_database_domain")
def set_database_domain(request: SetDatabaseDomainRequest):
    doctor_id = request.doctor_id
    
    session = manager.load_session_context(doctor_id, request.session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.domain = request.domain
    manager.save_session(session)
    
    return {"status": "ok", "domain": request.domain}


