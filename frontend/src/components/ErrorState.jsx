import { CloudOff, RotateCw } from "lucide-react";

export default function ErrorState({ message, onRetry, compact }) {
  return (
    <div className={`error-state ${compact ? "error-compact" : ""}`} role="alert">
      <span className="icon-tile tone-coral" aria-hidden="true">
        <CloudOff size={compact ? 18 : 26} />
      </span>
      <div className="error-text">
        <strong>We cannot reach the IronPass API</strong>
        <p>{message}</p>
      </div>
      <button type="button" className="btn btn-outline" onClick={onRetry}>
        <RotateCw size={16} aria-hidden="true" />
        <span>Try again</span>
      </button>
    </div>
  );
}
