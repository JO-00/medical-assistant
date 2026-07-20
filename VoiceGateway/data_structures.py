from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class ConversationHistory(BaseModel):
    doctor_id: int
    session_id: Optional[int] = None
    content: List[tuple[str, str]]
    timestamp: Optional[datetime] = None
    dynamic_context: str = ""
    detected_language: Optional[str] = None
    intent: Optional[str] = None
    last_response: Optional[str] = ""

    def to_dict(self):
        data = self.model_dump()
        if self.timestamp is not None:
            data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data):
        if data.get("timestamp"):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
