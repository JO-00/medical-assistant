import os

SESSION_SERVICE_URL = os.getenv("SESSION_SERVICE_URL", "http://session-service:8000")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-this-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
DB_DSN = os.getenv("DB_DSN", "postgresql://postgres:password@postgres:5432/medical")