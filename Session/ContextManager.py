from typing import List, Optional
from datetime import datetime
from language_detection import LanguageDetector
from Router import route
from data_structures import ConversationHistory
import time_detection




class ConversationHistories:
    def __init__(self):
        self.conversation_histories: List[ConversationHistory] = []


    def __repr__(self) -> str:
        if not self.conversation_histories:
            return "<ConversationHistories empty>"
        
        output = f"<ConversationHistories ({len(self.conversation_histories)} sessions):\n"
        for conv in self.conversation_histories:
            output += f"  doctor={conv.doctor_id}, session={conv.session_id}, "
            output += f"messages={len(conv.content)}, lang={conv.detected_language or 'unknown'}\n"
            if conv.content:
                preview = " ".join(conv.content[:3])  # First 3 messages
                if len(conv.content) > 3:
                    preview += "..."
                output += f"    [{preview}]\n"
        output += ">"
        return output
    

    def load_user_context (self , doctor_id : int) -> list[ConversationHistory] :
        return [conv for conv in self.conversation_histories if conv.doctor_id == doctor_id]
    
    
    def load_session_context(self, doctor_id: int, session_id: int) -> Optional[ConversationHistory]:
        for conv in self.conversation_histories:
            if conv.doctor_id == doctor_id and conv.session_id == session_id:
                return conv
        return None
    
    def create_new_session(self, doctor_id: int) -> ConversationHistory:
        user_convs = [conv for conv in self.conversation_histories 
                    if conv.doctor_id == doctor_id]
        session_id = max(conv.session_id for conv in user_convs) + 1 if user_convs else 1
        session = ConversationHistory(
            doctor_id = doctor_id,
            session_id = session_id,
            content = [],
            timestamp= datetime.now(),
            dynamic_context= "",
            detected_language = ""
        )
        self.conversation_histories.append(session)
        return session

    
    
    def append_message(self, doctor_id: int, session_id: int, message: str, sender: str = "USER") -> ConversationHistory:
        """Append message, conditionally insert absolute timestamps if it targets the DB, and return the session."""
        if not message.strip():
            return None
        
        session = self.load_session_context(doctor_id, session_id)
        if not session:
            session = self.create_new_session(doctor_id)
        
        # 1. Deduce running language
        lang = session.detected_language or "en"
        
        # 2. Initial routing pass using raw text to parse user intent
        dynamic_context, intent = route.inject_dynamic_context(message, lang)
        
        # 3. Conditional time insertion block for database intent
        processed_message = message
        if sender == "USER" and intent == "database":
            processed_message = time_detection.insert_time(message, lang)

        # 4. Save history records and state tracking
        session.content.append((sender, processed_message))
        session.timestamp = datetime.now()
        session.dynamic_context = dynamic_context
        session.intent = intent
        
        # 5. Language detection safety fallback pass
        if not session.detected_language:
            detector = LanguageDetector()
            detector.add_text(processed_message)
            session.detected_language = detector.get_language()
            
        return session