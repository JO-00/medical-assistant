export default function Logo({ tone = "ink" }) {
  const color = tone === "paper" ? "text-paper-raised" : "text-ink";
  return (
    <div className={`flex items-baseline gap-2 ${color}`}>
      <span className="font-display text-xl tracking-tight">Consult</span>
      <span className="h-1.5 w-1.5 rounded-full bg-sage" aria-hidden="true" />
    </div>
  );
}
