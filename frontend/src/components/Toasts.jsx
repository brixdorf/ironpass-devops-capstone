import { CircleAlert, CircleCheck } from "lucide-react";

// Messages that dismiss themselves (App removes them after a few seconds).
export default function Toasts({ toasts }) {
  return (
    <div className="toasts" role="status" aria-live="polite">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast-${t.kind}`} role={t.kind === "error" ? "alert" : undefined}>
          {t.kind === "ok" ? (
            <CircleCheck size={18} aria-hidden="true" />
          ) : (
            <CircleAlert size={18} aria-hidden="true" />
          )}
          <span>{t.text}</span>
        </div>
      ))}
    </div>
  );
}
