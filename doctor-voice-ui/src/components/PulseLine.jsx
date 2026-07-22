// The pulse line is this product's signature: a single motif that reads as
// both an ECG trace and a voice waveform, tying "clinician" and "voice call"
// together. It idles as a slow, calm heartbeat and can be re-used anywhere
// we want that identity to show up quietly.

export default function PulseLine({ className = "", tone = "sage" }) {
  const stroke = tone === "paper" ? "#F8FAF8" : "#4F7869";
  return (
    <svg
      viewBox="0 0 400 60"
      preserveAspectRatio="none"
      className={className}
      aria-hidden="true"
    >
      <path
        d="M0 30 H140 L155 30 L165 8 L178 52 L190 30 L205 30 L215 18 L225 30 H400"
        fill="none"
        stroke={stroke}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength="1"
        style={{
          strokeDasharray: 1,
          strokeDashoffset: 1,
          animation: "pulse-draw 3.2s ease-in-out infinite",
        }}
      />
      <style>{`
        @keyframes pulse-draw {
          0% { stroke-dashoffset: 1; opacity: 0.25; }
          45% { stroke-dashoffset: 0; opacity: 1; }
          70% { stroke-dashoffset: -0.02; opacity: 1; }
          100% { stroke-dashoffset: -1; opacity: 0.25; }
        }
      `}</style>
    </svg>
  );
}
