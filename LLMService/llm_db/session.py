import redis, json
from datetime import date, datetime

def convert_dates(obj):
    """Recursively convert date/datetime objects to ISO format strings"""
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_dates(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_dates(item) for item in obj]
    else:
        return obj

class DatabaseSession:

    VALID_STATUSES = {
        "FRESH",
        "WAITING_MISSING_FIELDS",
        "WAITING_CONFIRMATION",
    }

    def __init__(self, id_medecin, id_session):
        self.id_medecin = id_medecin
        self.id_session = id_session
        self.status = "FRESH"
        self.query_type = None          # SELECT / INSERT / UPDATE / DELETE
        self.generated_sql = None
        self.table = None               # Useful metadata
        self.missing_fields = set()     # INSERT only
        self.preview_result = None      # DELETE only
        self.clarification_history = []
        self.last_clarification_question = None

    def set_status(self, status):
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid session status: {status}")
        self.status = status

    def __repr__(self):
        return (
            f"DatabaseSession("
            f"id_medecin={self.id_medecin}, "
            f"id_session={self.id_session}, "
            f"status={self.status}, "
            f"query_type={self.query_type})"
        )
    
    def to_dict(self):
        return {
            "id_medecin": self.id_medecin,
            "id_session": self.id_session,
            "status": self.status,
            "query_type": self.query_type,
            "generated_sql": self.generated_sql,
            "table": self.table,
            "missing_fields": list(self.missing_fields),
            "preview_result": convert_dates(self.preview_result),  # Fixed: convert dates to strings
            "clarification_history": self.clarification_history,
            "last_clarification_question": self.last_clarification_question,
        }

    @classmethod
    def from_dict(cls, data):
        session = cls(
            data["id_medecin"],
            data["id_session"]
        )

        session.status = data["status"]
        session.query_type = data["query_type"]
        session.generated_sql = data["generated_sql"]
        session.table = data["table"]
        session.missing_fields = set(data["missing_fields"])
        session.preview_result = data["preview_result"]
        session.clarification_history = data["clarification_history"]
        session.last_clarification_question = data["last_clarification_question"]

        return session


class SessionManager:

    def __init__(self):
        self.redis = redis.Redis(
            host="redis",
            port=6379,
            decode_responses=True
        )

    def create_session(self, id_medecin, id_session):
        session = DatabaseSession(id_medecin, id_session)
        key = f"db:{id_medecin}:{id_session}"
        self.redis.set(key, json.dumps(session.to_dict()))
        return session

    def get_session(self, id_medecin, id_session):
        key = f"db:{id_medecin}:{id_session}"
        data = self.redis.get(key)
        if data is None:
            return self.create_session(id_medecin, id_session)
        return DatabaseSession.from_dict(json.loads(data))

    def save_session(self, session):
        key = f"db:{session.id_medecin}:{session.id_session}"
        self.redis.set(key, json.dumps(session.to_dict()))

    def delete_session(self, id_medecin, id_session):
        key = f"db:{id_medecin}:{id_session}"
        return self.redis.delete(key) > 0

    def get_all_doctor_sessions(self, id_medecin):
        sessions = []
        for key in self.redis.scan_iter(f"db:{id_medecin}:*"):
            data = self.redis.get(key)
            if data is not None:
                sessions.append(DatabaseSession.from_dict(json.loads(data)))
        return sessions