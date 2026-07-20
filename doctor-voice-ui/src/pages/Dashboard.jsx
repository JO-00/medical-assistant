import { useEffect, useState, useCallback } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { fetchConversations } from "../lib/api";

export default function Dashboard() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchConversations();
      setSessions(data);
    } catch (err) {
      setError("Couldn't load your call history.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar sessions={sessions} loading={loading} error={error} />
      <main className="flex-1 h-screen overflow-y-auto bg-paper">
        <Outlet context={{ sessions, refreshSessions: load }} />
      </main>
    </div>
  );
}
