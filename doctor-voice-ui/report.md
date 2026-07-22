# 📝 Post-Mortem: The Great WebRTC Voice Loop Lock of 2026

## 🎭 The Symptoms (What It Looked Like)
1. **Frontend Perfection:** The React frontend initiated WebRTC beautifully. Microphone access was granted, the SDP Offer went out, the SDP Answer came back, and the ICE Connection shifted confidently from `gathering` to `checking` and finally to `connected`.
2. **The Data Illusion:** The browser console was showing active outbound RTP audio packets (`outbound-rtp audio 442 32283`). Media data was flying to the backend.
3. **The Absolute Silence:** Despite a perfect handshake and data streaming *to* the backend, the backend returned dead silence. No STT logs, no Ollama activations, and zero audio streamed back.

---

## 🔍 The Deep-Dive & The Core Culprit

The backend framework was built using **FastAPI** combined with **FastRTC**. FastAPI operates entirely on an asynchronous event loop (`async/await`), while the original voice pipeline was written using classic synchronous blocking code:

**AH BOI ALSO DONT FORGET THAT "RUN CD app" YOU WROTE ON THE DOCKERFILE AND WHY ITS STUPID**
In Docker, `ARG` is a temporary variable used exclusively while building the image. 
`ENV` is a permanent variable used while the container is actively running.
in the docker compose building an image happens first, meaning compiling and everything happens first
therefore we avoid to load env vars into the container via the code inside that container for the ui part, because:
in config.js we have:
```js
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
export const RTC_BASE_URL = import.meta.env.VITE_RTC_BASE_URL || "http://localhost:8000";
export const WEBRTC_OFFER_PATH = import.meta.env.VITE_WEBRTC_OFFER_PATH || "/webrtc/offer";
```
so during compilation, vite variable is empty, so its auto set to http://localhost:8000 and same for the others
to avoid such a race condition we use ARG from docker, since ENV vars happen after build, ARG happens during build
**ARG does nothing but set an environment variable during the build phase and wipes it off completely**
this is why you generally see in dockerfiles:
```Dockerfile
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build # for example
```
because dockerfile is completely blind to environemnt variables from docker compose since they are invisible until build is over

because docker builds, meani
```python
# THE BUGGY WAY:
def echo(audio):
    transcript = stt_model.stt(audio)                   # <-- BLOCKS THE MAIN THREAD
    response = chat(model="qwen2.5:3b", messages=[...])  # <-- BLOCKS THE MAIN THREAD
    for audio_chunk in tts_model.stream_tts_sync(...): # <-- BLOCKS THE MAIN THREAD
        yield audio_chunk
```

**The Three Critical Upgrades we made:**
async def + yield: Converted the function into an asynchronous iterator so the frame handler could pipeline chunks natively.

`loop.run_in_executor(None, ...)`: Automatically spins up a background worker thread for the heavy AI processing (STT, LLM, TTS). The main thread remains 100% free to keep WebRTC stable and responsive.

`await asyncio.sleep(0.01)`: A tiny, deliberate breathing room between audio chunks that guarantees the event loop can flush the current data out to the network socket before handling the next chunk.

💡 **Lessons for Later You**
WebRTC is highly time-sensitive. If you block the main thread for even a fraction of a second, audio packets drop, connections stutter, or handlers drop dead.

Never run blocking AI models directly in an async framework. If a function doesn't have an await variant (like standard local ollama.chat or sync tts_model), always wrap it in an executor thread.

**old code**
```python
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time

# --- FASTRTC IMPORTS ---
from fastrtc import ReplyOnPause, Stream
from fastrtc.reply_on_pause import AlgoOptions
from ollama import chat
from voice import stt_model, tts_model

app = FastAPI()

# Enable CORS so your React frontend can reach the WebRTC signaling routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOCK DATA ---
MOCK_USERS = {
    "test@example.com": {
        "id": "user_123",
        "email": "test@example.com",
        "password": "password123",
        "name": "Jane Doe"
    }
}
ACTIVE_SESSIONS = {}

# --- FASTRTC ECHO HANDLER ---
def echo(audio):
    print("🎤 Starting STT...")
    transcript = stt_model.stt(audio)

    if not transcript.strip():
        print("⚠️ Empty transcript")
        return

    print(f"\n🔊 User said: {transcript}")
    print(f"📤 Sending to model: {transcript}\n")

    system_prompt = """
Tu es un agent IA français qui aide l'utilisateur.
Réponds uniquement en français.
Parle naturellement comme dans une conversation vocale.
Sois concis, évite les longues explications.
Ne dis pas que tu es une IA sauf si on te le demande.
"""
    print("🧠 Asking model...")
    response = chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ]
    )

    response_text = response["message"]["content"]
    print(f"🤖 Model response: {response_text}\n")
    print("🔊 Starting TTS...")

    for audio_chunk in tts_model.stream_tts_sync(response_text):
        yield audio_chunk

    print("✅ TTS finished")


# FastRTC algorithm configuration
algo_options = AlgoOptions(
    audio_chunk_duration=1.0,  # process larger chunks
    started_talking_threshold=0.2,
    speech_threshold=0.1
)

# Create the FastRTC stream
stream = Stream(
    ReplyOnPause(
        echo,
        algo_options=algo_options,
        can_interrupt=True
    ),
    modality="audio",
    mode="send-receive"
)

# --- MOUNT FASTRTC ROUTES ON FASTAPI ---
# This automatically registers:
# - POST /webrtc/offer
# - GET/POST /websocket/offer
# - etc.
stream.mount(app)


# --- STANDARD API ENDPOINTS ---

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")  # Adjusted path to match your log: /auth/login
def login(data: LoginRequest):
    time.sleep(0.5)
    user = MOCK_USERS.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    dummy_token = f"dummy-jwt-token-for-{user['id']}"
    ACTIVE_SESSIONS[dummy_token] = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"]
    }
    return {
        "token": dummy_token,
        "user": ACTIVE_SESSIONS[dummy_token]
    }


# Mock endpoint to stop the 404 error on GET /conversations
@app.get("/conversations")
def get_conversations(authorization: Optional[str] = Header(None)):
    # Return a sample mock payload to avoid UI issues
    return [
        {
            "session_mock_1": {
                "content": [
                    {"USER": "Bonjour, j'ai une question."},
                    {"ASSISTANT": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"}
                ],
                "timestamp": "2026-07-17T12:00:00Z",
                "detected_language": "fr"
            }
        }
    ]


@app.get("/api/user")
def get_current_user(authorization: Optional[str] = Header(None)):
    time.sleep(0.3)
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header provided")
    
    token = authorization.replace("Bearer ", "").strip()
    user_session = ACTIVE_SESSIONS.get(token)
    if not user_session:
        raise HTTPException(status_code=401, detail="Session expired or invalid token")
        
    return user_session
```
---
**new code**
```python
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import time
import asyncio

# --- FASTRTC IMPORTS ---
from fastrtc import ReplyOnPause, Stream
from fastrtc.reply_on_pause import AlgoOptions
from ollama import chat
from voice import stt_model, tts_model

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MOCK DATA ---
MOCK_USERS = {
    "test@example.com": {
        "id": "user_123",
        "email": "test@example.com",
        "password": "password123",
        "name": "Jane Doe"
    }
}
ACTIVE_SESSIONS = {}


# --- DIAGNOSTIC ECHO HANDLER ---
async def debug_echo_handler(audio):
    """
    We run this as an async generator so FastAPI can yield control back 
    to the network loop, preventing WebRTC packet starvation.
    """
    print("\n" + "🎧" * 30)
    print("⚡ [BACKEND TRIGGER] VAD pause detected! Starting pipeline...")
    
    # 1. STT Phase
    print("🎤 [1/4] Sending audio to STT model...")
    try:
        # Run synchronous STT in a threadpool so it doesn't block the main event loop
        loop = asyncio.get_running_loop()
        transcript = await loop.run_in_executor(None, stt_model.stt, audio)
    except Exception as e:
        print(f"❌ [STT ERROR] Failed to transcribe: {e}")
        return

    if not transcript or not transcript.strip():
        print("⚠️ [STT WARNING] Empty transcript received. Aborting response.")
        return

    print(f"📝 [STT SUCCESS] User said: \"{transcript}\"")

    # 2. LLM Phase
    print("🧠 [2/4] Querying Ollama (qwen2.5:3b)...")
    system_prompt = """
Tu es un agent IA français qui aide l'utilisateur.
Réponds uniquement en français.
Parle naturellement comme dans une conversation vocale.
Sois concis, évite les longues explications.
Ne dis pas que tu es une IA sauf si on te le demande.
"""
    try:
        # Run Ollama request in a threadpool
        response = await loop.run_in_executor(
            None, 
            lambda: chat(
                model="qwen2.5:3b",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript}
                ]
            )
        )
        response_text = response["message"]["content"]
        print(f"🤖 [LLM SUCCESS] Response: \"{response_text}\"")
    except Exception as e:
        print(f"❌ [LLM ERROR] Ollama query failed: {e}")
        return

    # 3. TTS Phase
    print("🔊 [3/4] Initializing TTS generation stream...")
    try:
        # We run the TTS generator on a separate thread and yield chunks asynchronously
        def get_tts_chunks():
            return list(tts_model.stream_tts_sync(response_text))
            
        chunks = await loop.run_in_executor(None, get_tts_chunks)
        print(f"📦 [TTS] Generated {len(chunks)} audio chunks.")
        
        print("📤 [4/4] Streaming audio chunks back over WebRTC track...")
        for i, audio_chunk in enumerate(chunks):
            yield audio_chunk
            # Yield control back to the event loop momentarily to keep WebRTC stable
            await asyncio.sleep(0.01)
            
        print("✅ [PIPELINE COMPLETE] Response sent successfully.")
        print("🎧" * 30 + "\n")
        
    except Exception as e:
        print(f"❌ [TTS ERROR] TTS Stream failed: {e}")


# FastRTC algorithm configuration
algo_options = AlgoOptions(
    audio_chunk_duration=1.0,  # Process larger chunks
    started_talking_threshold=0.2,
    speech_threshold=0.1
)

# Create the FastRTC stream using our async diagnostic wrapper
stream = Stream(
    ReplyOnPause(
        debug_echo_handler,
        algo_options=algo_options,
        can_interrupt=True
    ),
    modality="audio",
    mode="send-receive"
)

# Mount FastRTC routes on FastAPI
stream.mount(app)


# --- STANDARD API ENDPOINTS ---

class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/auth/login")
def login(data: LoginRequest):
    time.sleep(0.5)
    user = MOCK_USERS.get(data.email)
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    dummy_token = f"dummy-jwt-token-for-{user['id']}"
    ACTIVE_SESSIONS[dummy_token] = {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"]
    }
    return {
        "token": dummy_token,
        "user": ACTIVE_SESSIONS[dummy_token]
    }


@app.get("/conversations")
def get_conversations(authorization: Optional[str] = Header(None)):
    return [
        {
            "session_mock_1": {
                "content": [
                    {"USER": "Bonjour, j'ai une question."},
                    {"ASSISTANT": "Bonjour ! Comment puis-je vous aider aujourd'hui ?"}
                ],
                "timestamp": "2026-07-17T12:00:00Z",
                "detected_language": "fr"
            }
        }
    ]


@app.get("/api/user")
def get_current_user(authorization: Optional[str] = Header(None)):
    time.sleep(0.3)
    if not authorization:
        raise HTTPException(status_code=401, detail="No authorization header provided")
    
    token = authorization.replace("Bearer ", "").strip()
    user_session = ACTIVE_SESSIONS.get(token)
    if not user_session:
        raise HTTPException(status_code=401, detail="Session expired or invalid token")
        
    return user_session
```