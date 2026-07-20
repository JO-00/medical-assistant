export default function ChatBubbles({ content = [] }) {
  return (
    <div className="flex flex-col gap-3">
      {content.map((turn, i) => {
        const isUser = turn.role === "USER";
        return (
          <div
            key={i}
            className={`flex ${isUser ? "justify-end" : "justify-start"} animate-rise`}
            style={{ animationDelay: `${Math.min(i * 30, 300)}ms` }}
          >
            <div
              className={`max-w-[70%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-sm ${
                isUser
                  ? "bg-ink text-paper-raised rounded-br-sm"
                  : "bg-paper-raised border border-line text-ink rounded-bl-sm"
              }`}
            >
              {turn.text}
            </div>
          </div>
        );
      })}
    </div>
  );
}
