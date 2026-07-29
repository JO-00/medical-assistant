import { useParams, useOutletContext } from "react-router-dom";
import { Globe2, Clock, Send, Loader2, Database, X, Check, Zap } from "lucide-react";
import ChatBubbles from "../components/ChatBubbles";
import { useState, useRef, useEffect } from "react";
import { sendMessage, setDatabaseDomain, toggleDatabaseMode } from "../lib/api";
import { useAuth } from "../lib/auth";
import { DOMAIN_ICONS } from "../lib/icons";

const DOMAINS = [
  { id: "autodetect", label: "Autodetect", icon: DOMAIN_ICONS.autodetect, note: "not recommended" },
  { id: "patients", label: "Patients", icon: DOMAIN_ICONS.patients },
  { id: "appointments", label: "Appointments", icon: DOMAIN_ICONS.appointments },
  { id: "doctor_notes", label: "Doctor Notes", icon: DOMAIN_ICONS.doctor_notes },
  { id: "acte_medecin", label: "Medical Acts", icon: DOMAIN_ICONS.acte_medecin },
];

export default function ChatView() {
  const { id } = useParams();
  const { sessions, refreshSessions } = useOutletContext();
  const { user } = useAuth();
  const session = sessions.find((s) => String(s.id) === String(id));
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [optimisticMessages, setOptimisticMessages] = useState([]);
  const [dbModeActive, setDbModeActive] = useState(false);
  const [dbMenuOpen, setDbMenuOpen] = useState(false);
  const [selectedDomain, setSelectedDomain] = useState("autodetect");
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setDbMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSendMessage = async () => {
    if (!message.trim() || sending || !user) return;
    
    const userMessage = message.trim();
    setMessage("");
    setSending(true);
    
    setOptimisticMessages(prev => [...prev, {
      role: "USER",
      text: userMessage,
      isOptimistic: true
    }]);
    
    try {
      await sendMessage(user.id, parseInt(id), userMessage);
      await refreshSessions();
      setOptimisticMessages([]);
    } catch (error) {
      console.error("Failed to send message:", error);
      setOptimisticMessages(prev => prev.filter(msg => !msg.isOptimistic));
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleToggleDatabase = async () => {
    const newState = !dbModeActive;
    
    try {
      // Appel API pour activer/désactiver le mode DB
      await toggleDatabaseMode(parseInt(id), newState);
      
      setDbModeActive(newState);
      setDbMenuOpen(newState);
      
      if (!newState) {
        setSelectedDomain("autodetect");
      }
    } catch (error) {
      console.error("Failed to toggle database mode:", error);
    }
  };

  const handleSelectDomain = async (domainId) => {
    setSelectedDomain(domainId);
    setDbMenuOpen(false);
    
    try {
      await setDatabaseDomain(parseInt(id), domainId);
      console.log(`Domain set to: ${domainId}`);
    } catch (error) {
      console.error("Failed to set domain:", error);
    }
  };

  if (!session) {
    return (
      <div className="h-full flex items-center justify-center text-ink-faint text-sm">
        Session not found.
      </div>
    );
  }

  const allMessages = [
    ...session.content.map(msg => ({
      role: msg.role,
      text: msg.text
    })),
    ...optimisticMessages
  ];

  if (sending) {
    allMessages.push({
      role: "ASSISTANT",
      text: "•••",
      isLoading: true
    });
  }

  const selectedDomainData = DOMAINS.find(d => d.id === selectedDomain);

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 flex flex-col h-full">
      <header className="mb-6 pb-4 border-b border-line flex items-center justify-between shrink-0">
        <div>
          <h1 className="font-display text-xl text-ink">Session {session.id}</h1>
          <div className="mt-1 flex items-center gap-3 text-xs text-ink-faint font-mono">
            <span className="inline-flex items-center gap-1">
              <Clock size={12} />
              {session.timestamp ? new Date(session.timestamp).toLocaleString() : "—"}
            </span>
            {session.detectedLanguage && (
              <span className="inline-flex items-center gap-1">
                <Globe2 size={12} />
                {session.detectedLanguage}
              </span>
            )}
            {dbModeActive && selectedDomainData && (
              <span className="inline-flex items-center gap-1 text-sage text-xs font-medium">
                <Database size={12} />
                DB: {selectedDomainData.label}
              </span>
            )}
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto mb-4">
        <ChatBubbles content={allMessages} />
      </div>

      <div className="shrink-0 border-t border-line pt-4">
        <div className="flex gap-2">
          <div className="relative" ref={menuRef}>
            <button
              onClick={handleToggleDatabase}
              className={`rounded-lg border px-3 py-2.5 transition-colors ${
                dbModeActive 
                  ? "bg-sage/10 border-sage text-sage" 
                  : "border-line text-ink-faint hover:border-ink/30 hover:text-ink"
              }`}
              title="Toggle database mode"
            >
              <Database size={18} />
            </button>

            {dbMenuOpen && (
              <div className="absolute bottom-full mb-2 left-0 bg-paper-raised rounded-xl shadow-xl border border-line p-2 min-w-[220px] z-50">
                <div className="text-xs text-ink-faint px-3 py-1 border-b border-line mb-1">
                  Select database domain
                </div>
                {DOMAINS.map((domain) => (
                  <button
                    key={domain.id}
                    onClick={() => handleSelectDomain(domain.id)}
                    className={`
                      w-full text-left px-3 py-2 rounded-lg text-sm transition-colors
                      flex items-center gap-3
                      ${selectedDomain === domain.id 
                        ? "bg-sage/10 text-ink" 
                        : "hover:bg-paper-raised-hover text-ink"
                      }
                    `}
                  >
                    <span className="text-base">{domain.icon}</span>
                    <span className="flex-1">{domain.label}</span>
                    {domain.note && (
                      <span className="text-[10px] text-ink-faint/60 bg-amber-50 px-1.5 py-0.5 rounded">
                        {domain.note}
                      </span>
                    )}
                    {selectedDomain === domain.id && (
                      <Check size={14} className="text-sage" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="flex-1 rounded-lg border border-line bg-paper-raised px-4 py-2.5 text-sm text-ink placeholder:text-ink-faint/50 focus:outline-none focus:ring-2 focus:ring-sage/50"
            disabled={sending}
          />
          <button
            onClick={handleSendMessage}
            disabled={!message.trim() || sending}
            className="rounded-lg bg-ink text-paper-raised px-4 py-2.5 hover:bg-ink/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {sending ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
          </button>
        </div>
      </div>
    </div>
  );
}