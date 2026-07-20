import { useParams, useOutletContext } from "react-router-dom";
import { Globe2, Clock, Send, Loader2 } from "lucide-react";
import ChatBubbles from "../components/ChatBubbles";
import { useState } from "react";
import { sendMessage } from "../lib/api";
import { useAuth } from "../lib/auth";

export default function ChatView() {
  const { id } = useParams();
  const { sessions, refreshSessions } = useOutletContext();
  const { user } = useAuth();
  const session = sessions.find((s) => String(s.id) === String(id));
  const [message, setMessage] = useState("");
  const [sending, setSending] = useState(false);
  const [optimisticMessages, setOptimisticMessages] = useState([]);

  const handleSendMessage = async () => {
    if (!message.trim() || sending || !user) return;
    
    const userMessage = message.trim();
    setMessage("");
    setSending(true);
    
    // Add user message immediately (optimistic update)
    setOptimisticMessages(prev => [...prev, {
      role: "USER",
      text: userMessage,
      isOptimistic: true
    }]);
    
    try {
      await sendMessage(user.id, parseInt(id), userMessage);
      
      // Refresh to get the assistant's response
      await refreshSessions();
      
      // Clear optimistic messages since we got the real data
      setOptimisticMessages([]);
      
    } catch (error) {
      console.error("Failed to send message:", error);
      // Remove the optimistic message on error
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

  if (!session) {
    return (
      <div className="h-full flex items-center justify-center text-ink-faint text-sm">
        Session not found.
      </div>
    );
  }

  // Combine real messages with optimistic ones
  const allMessages = [
    ...session.content.map(msg => ({
      role: msg.role,
      text: msg.text
    })),
    ...optimisticMessages
  ];

  // Add loading dots if sending (assistant is thinking)
  if (sending) {
    allMessages.push({
      role: "ASSISTANT",
      text: "•••",
      isLoading: true
    });
  }

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
          </div>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto mb-4">
        <ChatBubbles content={allMessages} />
      </div>

      {/* Message Input */}
      <div className="shrink-0 border-t border-line pt-4">
        <div className="flex gap-2">
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