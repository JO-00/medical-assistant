import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import { useState, useEffect } from "react";
import { fetchConversations } from "../lib/api";

export default function Layout() {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadSessions = async () => {
      try {
        setLoading(true);
        const data = await fetchConversations();
        setSessions(data);
        setError(null);
      } catch (err) {
        setError(err.message || "Failed to load conversations");
      } finally {
        setLoading(false);
      }
    };
    loadSessions();
  }, []);

  return (
    <div className="flex h-screen">
      <Sidebar 
        sessions={sessions} 
        loading={loading} 
        error={error} 
      />
      <main className="flex-1 overflow-y-auto bg-paper">
        <Outlet context={{ sessions, setSessions }} />
      </main>
    </div>
  );
}