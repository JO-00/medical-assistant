from fastapi import FastAPI, Depends, Request,HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router, get_current_user
import logging,requests
from context import current_doctor_id
logger = logging.getLogger(__name__)
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

# Create a single stream that uses the context variable
# This requires modifying voice_pipeline.py to use context
from voice_pipeline import create_voice_pipeline_with_context
stream = create_voice_pipeline_with_context()

@app.middleware("http")
async def set_doctor_context(request: Request, call_next):
    """Middleware to set doctor_id from auth header"""
    authorization = request.headers.get("authorization")
    if authorization:
        try:
            user = get_current_user(authorization)
            doctor_id = user["id"]
            current_doctor_id.set(doctor_id)
        except:
            pass
    response = await call_next(request)
    return response

@app.get("/api/user")
def get_user_endpoint(current_user: dict = Depends(get_current_user)):
    return current_user


@app.get("/conversations")
def get_conversations(current_user: dict = Depends(get_current_user)):
    response = requests.get(
        os.getenv("SESSION_SERVICE_URL") + "/conversations",
        params=current_user  # Sends as query params: ?id=123&username=dr_smith...
    )
    return response.json()





class TextRequest(BaseModel):
    doctor_id: int
    session_id: int
    message: str

@app.post("/text_session")
def text_session(
    request: TextRequest, 
    current_user: dict = Depends(get_current_user)  # JWT authentication
):
    if current_user["id"] != request.doctor_id:
        raise HTTPException(status_code=403, detail="You can only access your own sessions")
    
    # Forward to session service
    response = requests.post(
        os.getenv("SESSION_SERVICE_URL") + "/session",
        json={
            "doctor_id": request.doctor_id,
            "session_id": request.session_id,
            "message": request.message
        }
    )
    
    # Return the response from session service
    return response.json()




@app.get('/health')
def im_healthy():
    return {"response": "healthy"}

# Mount the WebRTC stream globally
# The stream will use current_doctor_id from context
stream.mount(app)