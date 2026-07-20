from fastapi import APIRouter
from pydantic import BaseModel
from llm_db.session import SessionManager
from llm_db.sql_agent import sql_agent
session_manager = SessionManager()

router = APIRouter()

class ContinueDBSessionRequest(BaseModel):
    doctor_id: int
    session_id: int
    message: str


@router.post("/continue_db_session")
def continue_db_session(
    request: ContinueDBSessionRequest
):

    session = session_manager.get_session(
        request.doctor_id,
        request.session_id
    )

    result = sql_agent(
        request.message,
        session,
        session_manager
    )

    return {
        "response": result
    }
def handle_database_request(session):

    db_session = session_manager.get_session(
        session.doctor_id,
        session.session_id
    )

    return sql_agent(
        session.content[-1][1],
        db_session,
        session_manager
    )

