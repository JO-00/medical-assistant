from fastapi import FastAPI
from pydantic import BaseModel
from session_management import handle_input
from ContextManager import ConversationHistory
from typing import Optional

app = FastAPI()


class Req (BaseModel):
    doctor_id : int
    session_id : Optional[int] = None
    message : str



@app.post("/session")
def handle_session(request : Req) -> ConversationHistory :
    return handle_input(request.model_dump())

