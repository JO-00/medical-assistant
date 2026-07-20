import { NavLink } from "react-router-dom";
import { Phone, LogOut, Loader2 } from "lucide-react";
import Logo from "./Logo";
import { useAuth } from "../lib/auth";

function formatTimestamp(ts) {
  if (!ts) return "Untitled session";
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  const datePart = sameDay
    ? "Today"
    : d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  const timePart = d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  return `${datePart} · ${timePart}`;
}

export default function Sidebar({ sessions, loading, error }) {
  const { logout } = useAuth();

  return (
    <aside className="w-72 shrink-0 h-screen bg-ink text-paper-raised flex flex-col">
      <div className="px-5 pt-5 pb-4">
        <Logo tone="paper" />
      </div>

      <div className="px-4">
        <NavLink
          to="/call"
          className={({ isActive }) =>
            `flex items-center gap-2 rounded-lg px-4 py-3 text-sm font-medium transition-colors ${
              isActive ? "bg-sage text-ink" : "bg-sage/90 hover:bg-sage text-ink"
            }`
          }
        >
          <Phone size={16} />
          New call
        </NavLink>
      </div>

      <div className="mt-6 px-5 text-xs font-mono uppercase tracking-widest text-paper-raised/40">
        Sessions
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-1">
        {loading && (
          <div className="flex items-center gap-2 px-2 py-3 text-sm text-paper-raised/50">
            <Loader2 size={14} className="animate-spin" />
            Loading history…
          </div>
        )}

        {error && !loading && (
          <div className="px-2 py-3 text-sm text-brick-soft">{error}</div>
        )}

        {!loading && !error && sessions.length === 0 && (
          <div className="px-2 py-3 text-sm text-paper-raised/45 leading-relaxed">
            No calls yet. Start one and it'll show up here.
          </div>
        )}

        {sessions.map((session) => (
          <NavLink
            key={session.id}
            to={`/session/${session.id}`}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2.5 transition-colors ${
                isActive ? "bg-ink-soft" : "hover:bg-ink-soft/60"
              }`
            }
          >
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-medium truncate">
                {formatTimestamp(session.timestamp)}
              </span>
              {session.detectedLanguage && (
                <span className="shrink-0 text-[10px] font-mono uppercase tracking-wide text-sage-light bg-sage/15 rounded px-1.5 py-0.5">
                  {session.detectedLanguage}
                </span>
              )}
            </div>
            <p className="mt-0.5 text-xs text-paper-raised/45 truncate">
              {previewOf(session)}
            </p>
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-ink-soft">
        <button
          onClick={logout}
          className="flex items-center gap-2 text-sm text-paper-raised/60 hover:text-paper-raised transition-colors"
        >
          <LogOut size={15} />
          Log out
        </button>
      </div>
    </aside>
  );
}

function previewOf(session) {
  const firstUser = session.content?.find((t) => t.sender === "USER");
  return firstUser?.message || "No transcript yet";
}
