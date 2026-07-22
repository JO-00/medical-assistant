from contextvars import ContextVar

current_doctor_id = ContextVar(
    "current_doctor_id",
    default=1
)