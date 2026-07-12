from ContextManager import ConversationHistories 
from data_structures import ConversationHistory
import json
import LLM_API

# Create instance
manager = ConversationHistories()

def get_session(input_data: dict) -> ConversationHistory:
    if 'doctor_id' not in input_data:
        raise ValueError("missing doctor_id")
    
    doctor_id = input_data["doctor_id"]
    session_id = input_data.get("session_id")
    
    if session_id:
        session = manager.load_session_context(doctor_id, session_id)
        if session:  # If session exists, return it
            return session
        else:  # Session doesn't exist, create new one
            return manager.create_new_session(doctor_id)
    return manager.create_new_session(doctor_id)
   

def handle_input(input_data: dict) -> ConversationHistory:
    
    if 'doctor_id' not in input_data or 'message' not in input_data:
        raise ValueError("Missing fields")
    
    doctor_id = input_data["doctor_id"]
    session_id = input_data.get("session_id")
    message = input_data["message"]
    
    if session_id:
        session = manager.load_session_context(doctor_id, session_id)
        if not session:
            session = manager.create_new_session(doctor_id)
    else:
        session = manager.create_new_session(doctor_id)
    
    session = LLM_API.call_inference(manager.append_message(doctor_id, session.session_id, message))
    manager.append_message(doctor_id = session.doctor_id , session_id= session.session_id , message = session.last_response , sender = "Assistant")
    return session
    



if __name__ == "__main__":
    print('TEST TEST')
    while True:
        raw = input("enter JSON: ")
        data = json.loads(raw)
        print(f"insertion result = {handle_input(data)}")
