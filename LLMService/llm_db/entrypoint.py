from fastapi import APIRouter
from pydantic import BaseModel
from llm_db.session import SessionManager
from llm_db.llm_service import SQLGenerator
import ollama
from typing import Optional , List 
from datetime import datetime
session_manager = SessionManager()

router = APIRouter()

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

def handle_database_request(session):

    db_session = session_manager.get_session(
        session.doctor_id,
        session.session_id
    )

    return SQLGenerator.generate_and_execute(
        session.content[-1][1],
        db_session,
        session.domain
    )

def handle_conversational_request(session: ConversationHistory):
    with open("llm_db/prompts/conversational_prompt.txt", "r") as f:
        system_prompt = f.read()
    
    full_prompt = f"""{system_prompt}

        Maintenant, répondez à cette requête: {session.content[-1][1]}

        Assistant: """
            
    response = ollama.chat(
        model="qwen2.5:1.5b",
        messages=[{"role": "user", "content": full_prompt}],
        options={
                    "num_ctx": 800,
                    "num_gpu": 0
                }
    )
    
    return response['message']['content'].strip()


# test
if __name__ == '__main__':
    print("Assistant conversationnel. CTRL+C pour quitter.")
    
    session = ConversationHistory(
        doctor_id=1,
        session_id=1,
        content=[],
        domain="system"
    )
    
    try:
        while True:
            user_input = input("\nVous: ")
            session.content.append(("USER", user_input))
            
            response = handle_conversational_request(session)
            session.content.append(("ASSISTANT", response))
            
            print(f"Assistant: {response}")
    except KeyboardInterrupt:
        print("\nAu revoir !")





        