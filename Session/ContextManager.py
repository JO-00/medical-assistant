from typing import Optional
from datetime import datetime
from data_structures import ConversationHistory
import logging,redis,json
from LLM_API import *

logger = logging.getLogger()

class ConversationHistories:
    def __init__(self):
        self.redis = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )

    def __repr__(self) -> str:
        sessions = []
        for key in self.redis.scan_iter("conversation:*"):
            data = self.redis.get(key)
            if data:
                sessions.append(
                    ConversationHistory.from_dict(
                        json.loads(data)
                    )
                )
        if not sessions:
            return "<ConversationHistories empty>"
        output = f"<ConversationHistories ({len(sessions)} sessions):\n"
        for conv in sessions:
            output += (
                f"  doctor={conv.doctor_id}, "
                f"session={conv.session_id}, "
                f"messages={len(conv.content)}, "
                f"lang={conv.detected_language or 'unknown'}\n"
            )
            if conv.content:
                preview = " ".join(
                    msg for _, msg in conv.content[:3]
                )
                if len(conv.content) > 3:
                    preview += "..."
                output += f"    [{preview}]\n"
        output += ">"
        return output

    def save_session(self, session: ConversationHistory):
        key = f"conversation:{session.doctor_id}:{session.session_id}"
        self.redis.set(
            key,
            json.dumps(session.to_dict())
        )

    def load_user_context(self, doctor_id: int) -> list[ConversationHistory]:
        sessions = []
        for key in self.redis.scan_iter(f"conversation:{doctor_id}:*"):
            data = self.redis.get(key)
            if data:
                sessions.append(
                    ConversationHistory.from_dict(
                        json.loads(data)
                    )
                )
        return sessions

    def load_session_context(
        self,
        doctor_id: int,
        session_id: int
    ) -> Optional[ConversationHistory]:
        key = f"conversation:{doctor_id}:{session_id}"
        data = self.redis.get(key)
        if data is None:
            return None
        return ConversationHistory.from_dict(
            json.loads(data)
        )

    def create_new_session(
        self,
        doctor_id: int
    ) -> ConversationHistory:
        sessions = self.load_user_context(doctor_id)
        session_id = (
            max(conv.session_id for conv in sessions) + 1
            if sessions
            else 1
        )
        session = ConversationHistory(
            doctor_id=doctor_id,
            session_id=session_id,
            content=[],
            timestamp=datetime.now(),
            dynamic_context="",
            detected_language=""
        )
        self.save_session(session)
        return session

    def append_message(
        self,
        doctor_id: int,
        session_id: int,
        message: str,
        sender: str = "USER"
    ) -> ConversationHistory:
        
        if not message.strip():
            return None

        session = self.load_session_context(
            doctor_id,
            session_id
        )

        if session is None:
            session = self.create_new_session(
                doctor_id
            )

        session.content.append(
            (sender, message)
        )
        session.timestamp = datetime.now()
        self.save_session(session)
        return session
