// Central place to point the UI at your backend.
// Override these by creating a .env file (see .env.example) —
// Vite only exposes variables prefixed with VITE_.

// Base URL for your REST API (auth, patients, conversation history, etc.)
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
// Base URL for your fastrtc server (the app that mounts `stream`).
// If you mount fastrtc directly onto the same FastAPI app as your REST API,
// this can be the same as API_BASE_URL.
export const RTC_BASE_URL = import.meta.env.VITE_RTC_BASE_URL || "http://localhost:8000";

// fastrtc's built-in FastAPI mount (stream.mount(app)) exposes signaling at
// POST {RTC_BASE_URL}/webrtc/offer by default. Change this if you customized it.
export const WEBRTC_OFFER_PATH = import.meta.env.VITE_WEBRTC_OFFER_PATH || "/webrtc/offer";
