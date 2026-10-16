import { useEffect, useState } from "react";
import { UserPlus } from "lucide-react";
import Logo from "./Logo.jsx";

// The chip asks the backend /health (through the frontend server) every 15 s.
function useApiHealth() {
  const [state, setState] = useState("checking");
  useEffect(() => {
    let alive = true;
    async function ping() {
      try {
        const response = await fetch("/backend-health", { cache: "no-store" });
        const body = await response.json();
        if (alive) setState(response.ok && body.status === "ok" ? "up" : "down");
      } catch {
        if (alive) setState("down");
      }
    }
    ping();
    const timer = setInterval(ping, 15000);
    return () => {
      alive = false;
      clearInterval(timer);
    };
  }, []);
  return state;
}

const CHIP_TEXT = { checking: "Checking API", up: "API UP", down: "API down" };

export default function Header({ onSignup }) {
  const health = useApiHealth();
  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <Logo />
          <div>
            <h1 className="wordmark">
              Iron<b>Pass</b>
            </h1>
            <span className="tagline">Gym membership desk</span>
          </div>
        </div>
        <div className="topbar-actions">
          <span className={`status-chip status-${health}`} role="status" aria-live="polite">
            <span className="dot" aria-hidden="true" />
            {CHIP_TEXT[health]}
          </span>
          <button type="button" className="btn btn-outline" aria-label="New signup" onClick={onSignup}>
            <UserPlus size={18} aria-hidden="true" />
            <span>New signup</span>
          </button>
        </div>
      </div>
    </header>
  );
}
