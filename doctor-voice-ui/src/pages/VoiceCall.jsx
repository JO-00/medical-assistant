import { useCallback, useEffect, useRef, useState } from "react";
import { useNavigate, useOutletContext } from "react-router-dom";
import { Phone, PhoneOff, Mic, MicOff, Loader2, AlertCircle } from "lucide-react";
import PulseLine from "../components/PulseLine";
import CallWaveform from "../components/CallWaveform";
import { RTC_BASE_URL, WEBRTC_OFFER_PATH } from "../config";

const STATUS_COPY = {
  idle: "Ready when you are",
  connecting: "Connecting…",
  connected: "On call",
  ended: "Call ended",
};

export default function VoiceCall() {
  const [status, setStatus] = useState("idle");
  const [muted, setMuted] = useState(false);
  const [error, setError] = useState("");
  const [duration, setDuration] = useState(0);

  const pcRef = useRef(null);
  const localStreamRef = useRef(null);
  const remoteAudioRef = useRef(null);
  const timerRef = useRef(null);
  const startedAtRef = useRef(null);
  const dataChannelRef = useRef(null);

  const navigate = useNavigate();
  const { refreshSessions } = useOutletContext();

  const cleanup = useCallback(() => {
    clearInterval(timerRef.current);
    timerRef.current = null;

    localStreamRef.current?.getTracks().forEach((track) => track.stop());
    localStreamRef.current = null;

    if (dataChannelRef.current) {
      dataChannelRef.current.close();
      dataChannelRef.current = null;
    }
    if (pcRef.current) {
      pcRef.current.close();
      pcRef.current = null;
    }
  }, []);

  useEffect(() => () => cleanup(), [cleanup]);

  const startCall = async () => {
  setError("");
  setStatus("connecting");
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    localStreamRef.current = stream;

    const pc = new RTCPeerConnection({
      iceServers: [{ urls: "stun:stun.l.google.com:19302" }],
    });
    pcRef.current = pc;

    const dataChannel = pc.createDataChannel("text");
    dataChannelRef.current = dataChannel;

    stream.getTracks().forEach((track) => pc.addTrack(track, stream));

    pc.ontrack = (event) => {
      console.log("TRACK", event.track.kind, event.track.readyState);

      event.track.onended = () => {
        console.log("REMOTE TRACK ENDED");
      };

      event.track.onmute = () => {
        console.log("REMOTE TRACK MUTED");
      };

      event.track.onunmute = () => {
        console.log("REMOTE TRACK UNMUTED");
      };

      if (!remoteAudioRef.current) {
        console.log("No audio element!");
        return;
      }

      let remoteStream;

      if (event.streams && event.streams[0]) {
        remoteStream = event.streams[0];
      } else {
        remoteStream = new MediaStream([event.track]);
      }

      console.log("REMOTE STREAM", remoteStream);

      remoteAudioRef.current.srcObject = remoteStream;
      remoteAudioRef.current.volume = 1.0;

      remoteAudioRef.current.play()
        .then(() => console.log("AUDIO PLAYING"))
        .catch((err) => {
          console.error("AUDIO PLAY FAILED:", err);
          setError("Audio blocked. Click anywhere to enable playback.");
        });
    };

    
    
    pc.oniceconnectionstatechange = () => {
      console.log("ICE state:", pc.iceConnectionState);
    };
    
    pc.onsignalingstatechange = () => {
      console.log("SIGNAL state:", pc.signalingState);
    };

    pc.onicecandidate = (e) => {
      if (e.candidate) {
        console.log("ICE candidate:", e.candidate);
      }
    };

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    await waitForIceGathering(pc);

    const webrtcId = crypto.randomUUID();
    const res = await fetch(`${RTC_BASE_URL}${WEBRTC_OFFER_PATH}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        sdp: pc.localDescription.sdp,
        type: pc.localDescription.type,
        webrtc_id: webrtcId,
      }),
    });

    if (!res.ok) throw new Error(`Signaling failed (${res.status})`);
    
    const answer = await res.json();
    await pc.setRemoteDescription(new RTCSessionDescription(answer));

    setStatus("connected");
    startedAtRef.current = Date.now();
    timerRef.current = setInterval(() => {
      setDuration(Math.floor((Date.now() - startedAtRef.current) / 1000));
    }, 1000);

  } catch (err) {  // ← THIS must be OUTSIDE the try block
    setError(
      err.name === "NotAllowedError"
        ? "Microphone access blocked. Please allow permissions."
        : "Couldn't reach the assistant. Check your backend status."
    );
    setStatus("idle");
    cleanup();
  }
};
  

  const endCall = () => {
    cleanup();
    setStatus("ended");
    setDuration(0);
    refreshSessions?.();
  };

  const toggleMute = () => {
      const track = localStreamRef.current?.getAudioTracks()[0];
      if (track) {
        setMuted((prev) => {
          // If currently muted (true), enable the track (false)
          // If currently not muted (false), disable the track (true)
          track.enabled = prev;  // When prev=true (muted), track.enabled=false (disabled)
          return !prev;
        });
      }
    };

  return (
    <div className="h-full flex flex-col items-center justify-center px-6">
      <audio ref={remoteAudioRef} autoPlay />

      <div className="w-full max-w-md text-center">
        <p className="text-xs font-mono uppercase tracking-widest text-sage mb-3">
          {STATUS_COPY[status]}
          {status === "connected" && ` · ${formatDuration(duration)}`}
        </p>

        <h1 className="font-display text-2xl text-ink mb-8">
          {status === "connected" ? "Talking with your assistant" : "Start a new call"}
        </h1>

        <div className="relative h-28 mb-10 rounded-2xl border border-line bg-paper-raised overflow-hidden flex items-center justify-center">
          {status === "connected" ? (
            <CallWaveform stream={localStreamRef.current} active color="#4F7869" />
          ) : (
            <PulseLine
              className={`h-10 w-64 ${status === "connecting" ? "animate-breathe" : "opacity-50"}`}
            />
          )}
        </div>

        {error && (
          <div className="mb-6 flex items-start gap-2 rounded-lg bg-brick-soft/60 border border-brick/30 px-4 py-3 text-sm text-brick text-left">
            <AlertCircle size={16} className="mt-0.5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex items-center justify-center gap-4">
          {status === "connected" && (
            <button
              onClick={toggleMute}
              className={`h-14 w-14 rounded-full flex items-center justify-center border transition-colors ${
                muted
                  ? "bg-brick-soft border-brick/30 text-brick"
                  : "bg-paper-raised border-line text-ink hover:bg-paper"
              }`}
              aria-label={muted ? "Unmute" : "Mute"}
            >
              {muted ? <MicOff size={20} /> : <Mic size={20} />}
            </button>
          )}

          {status === "connected" ? (
            <button
              onClick={endCall}
              className="h-16 w-16 rounded-full bg-brick text-paper-raised flex items-center justify-center shadow-card hover:opacity-90 transition-opacity"
              aria-label="End call"
            >
              <PhoneOff size={22} />
            </button>
          ) : (
            <button
              onClick={startCall}
              disabled={status === "connecting"}
              className="h-16 w-16 rounded-full bg-sage text-ink flex items-center justify-center shadow-card hover:opacity-90 transition-opacity disabled:opacity-70"
              aria-label="Start call"
            >
              {status === "connecting" ? (
                <Loader2 size={22} className="animate-spin" />
              ) : (
                <Phone size={22} />
              )}
            </button>
          )}
        </div>

        {status === "ended" && (
          <button
            onClick={() => navigate("/")}
            className="mt-8 text-sm text-ink-faint hover:text-ink transition-colors"
          >
            Back to sessions
          </button>
        )}
      </div>
    </div>
  );
}

function waitForIceGathering(pc) {
  if (pc.iceGatheringState === "complete") return Promise.resolve();
  
  return new Promise((resolve) => {
    const check = () => {
      // 🟢 Fix: Only resolve when gathering is fully complete
      if (pc.iceGatheringState === "complete") {
        pc.removeEventListener("icegatheringstatechange", check);
        resolve();
      }
    };
    
    pc.addEventListener("icegatheringstatechange", check);
    
    // Safety timeout: If it takes too long to find every public port, 
    // proceed after 1 second with what we have
    setTimeout(() => {
      pc.removeEventListener("icegatheringstatechange", check);
      resolve();
    }, 1000);
  });
}

function formatDuration(totalSeconds) {
  const m = String(Math.floor(totalSeconds / 60)).padStart(2, "0");
  const s = String(totalSeconds % 60).padStart(2, "0");
  return `${m}:${s}`;
}