import { Link } from "react-router-dom";
import { Phone } from "lucide-react";
import PulseLine from "../components/PulseLine";

export default function EmptyState() {
  return (
    <div className="h-full flex flex-col items-center justify-center text-center px-6">
      <PulseLine className="h-10 w-56 mb-6 opacity-70" />
      <h1 className="font-display text-2xl text-ink mb-2">Nothing selected yet</h1>
      <p className="text-ink-faint max-w-sm mb-6">
        Choose a past call from the sidebar, or start a new one — the assistant can pull up
        today's patients, flag conflicts, or add someone new while you talk.
      </p>
      <Link
        to="/call"
        className="inline-flex items-center gap-2 rounded-lg bg-ink text-paper-raised font-medium px-5 py-3 hover:bg-ink-soft transition-colors"
      >
        <Phone size={16} />
        Start a call
      </Link>
    </div>
  );
}
