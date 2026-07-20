# Consult — Doctor Voice Assistant UI

React (Vite) frontend for a voice-first clinical assistant: manual sign up/login,
a sidebar of past call sessions rendered as chat bubbles, and a "new call" screen
that opens a WebRTC connection to your `fastrtc` backend.

## Run it

```bash
npm install
cp .env.example .env   # point at your backend
npm run dev
```

## Backend contract

The UI is decoupled from your backend via `src/config.js` and `src/lib/api.js`.
Point `VITE_API_BASE_URL` / `VITE_RTC_BASE_URL` at your FastAPI app and implement
these routes (adjust `src/lib/api.js` if your paths differ):

### Auth

- `POST /auth/login` — body `{ email, password }` → `{ access_token }`
- `POST /auth/signup` — body: everything collected on the signup form —
  `full_name`, `email`, `password`, `qualification`, `specialty`,
  `license_number`, `years_of_experience`, `clinic_name`, `phone_number`,
  `languages_spoken` (array), `timezone`, `bio` → `{ access_token }`

The token is stored in `localStorage` and sent as `Authorization: Bearer <token>`
on every request. A `401` anywhere clears it and bounces to `/login`.

### Conversation history

- `GET /conversations` — returns your `ConversationHistory` list, e.g.:

```json
[
  {
    "session_1": {
      "content": [{"USER": "..."}, {"ASSISTANT": "..."}],
      "timestamp": "2026-07-17T10:32:00Z",
      "detected_language": "fr"
    }
  }
]
```

`src/lib/api.js#normalizeConversations` flattens this into the shape the UI
renders — sidebar entries sorted by timestamp, each opening into a bubble view.

### Voice call (fastrtc)

`VoiceCall.jsx` speaks plain WebRTC to whatever `stream.mount(app)` exposes
in `fastrtc` — by default `POST {RTC_BASE_URL}/webrtc/offer` with
`{ sdp, type, webrtc_id }`, answered with `{ sdp, type }`. It:

1. Asks for mic permission and opens an `RTCPeerConnection`.
2. Waits for ICE gathering to finish (non-trickle, matching fastrtc's usual demo setup).
3. Posts the offer, applies the answer, and plays the returned audio track.
4. Live-visualizes the mic input on a canvas waveform while connected.

If your `webrtc/offer` path or payload shape differs, adjust
`WEBRTC_OFFER_PATH` in `.env` or edit `startCall()` in `VoiceCall.jsx` directly.

Patient add/remove/lookup happens on your backend during the call itself (per
your `echo()` handler) — there's no separate patient-management screen here by
design, since the doctor manages patients by talking to the assistant.

## Structure

```
src/
  config.js            API/WebRTC base URLs (env-driven)
  lib/
    api.js             axios instance, JWT handling, auth + conversations calls
    auth.jsx           React context wrapping login/signup/logout
  components/
    PulseLine.jsx       signature idle waveform/ECG motif
    CallWaveform.jsx     live mic-driven canvas waveform
    Sidebar.jsx           session list + new call button
    ChatBubbles.jsx       renders a session's USER/ASSISTANT turns
    ProtectedRoute.jsx    redirects unauthenticated visitors to /login
    Logo.jsx
  pages/
    Login.jsx
    Signup.jsx             full doctor profile form
    Dashboard.jsx           sidebar + <Outlet/> shell
    EmptyState.jsx          default panel, no session selected
    ChatView.jsx            one session's transcript
    VoiceCall.jsx           the call screen
```
