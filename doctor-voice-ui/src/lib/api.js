import axios from "axios";
import {API_BASE_URL}  from "../config";

// ---- Send Message using SESSION_LOCAL_ENDPOINT --------------------------

const TOKEN_KEY = "consult_jwt";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.request.use((cfg) => {
  const token = getToken();
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err?.response?.status === 401) {
      clearToken();
      if (!location.pathname.startsWith("/login")) {
        location.assign("/login");
      }
    }
    return Promise.reject(err);
  }
);

// ---- Auth -----------------------------------------------------------

/**
 * Expected backend contract (adjust paths to match your FastAPI routes):
 * POST /auth/login   { email, password }              -> { access_token }
 * POST /auth/signup  { ...signupPayload }              -> { access_token }
 */
export async function login({ email, password }) {
  const { data } = await api.post("/auth/login", { email, password });
  return data;
}

export async function signup(payload) {
  const { data } = await api.post("/auth/signup", payload);
  return data;
}

// ---- Conversations ----------------------------------------------------

/**
 * GET /conversations -> array shaped like ConversationHistory, e.g.
 * [{ session_1: { content: [{USER:"..."},{ASSISTANT:"..."}], timestamp, detected_language } }, ...]
 * This client normalizes that shape into a flat array of session objects.
 */
export async function fetchConversations() {
  const { data } = await api.get("/conversations");
  return normalizeConversations(data);
}

export function normalizeConversations(raw) {
  if (!Array.isArray(raw)) return [];
  
  // Your API already returns the correct format
  return raw
    .map((session) => {
      // Your API uses "sender" and "message"
      const content = (session.content || []).map((turn) => ({
        role: turn.sender.toUpperCase(),  // Map sender → role
        text: turn.message                // Map message → text
      }));
      
      return {
        id: session.id,
        content,
        timestamp: session.timestamp,
        detectedLanguage: session.detectedLanguage || session.detected_language,
      };
    })
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

// ---- Send Message ----------------------------------------------------

export async function sendMessage(doctorId, sessionId, message) {
  const { data } = await api.post("/text_session", {
    doctor_id: doctorId,
    session_id: sessionId,
    message: message
  });
  return data;
}

