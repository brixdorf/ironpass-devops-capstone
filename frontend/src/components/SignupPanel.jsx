import { useState } from "react";
import { X } from "lucide-react";
import { useDialog } from "../hooks/useDialog.js";

const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

function validate({ fullName, email }) {
  const errors = {};
  if (fullName.trim().length < 2) errors.fullName = "Enter the full name, at least 2 letters.";
  if (!EMAIL.test(email.trim())) errors.email = "Enter a valid email such as name@example.com.";
  return errors;
}

// Slide-over panel with the signup form.
export default function SignupPanel({ open, plans, onClose, onCreate }) {
  const ref = useDialog(open, onClose);
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [planId, setPlanId] = useState("");
  const [touched, setTouched] = useState({});
  const [busy, setBusy] = useState(false);
  const [apiError, setApiError] = useState("");

  const errors = validate({ fullName, email });
  const show = (field) => touched[field] && errors[field];

  async function submit(event) {
    event.preventDefault();
    setTouched({ fullName: true, email: true });
    if (Object.keys(errors).length > 0) return;
    setBusy(true);
    setApiError("");
    const outcome = await onCreate({
      full_name: fullName,
      email,
      plan_id: Number(planId || plans[0]?.id),
    });
    setBusy(false);
    if (outcome.ok) {
      setFullName("");
      setEmail("");
      setPlanId("");
      setTouched({});
    } else {
      setApiError(outcome.error);
    }
  }

  return (
    <div className={`overlay ${open ? "overlay-open" : ""}`} aria-hidden={!open} onMouseDown={onClose}>
      <div
        ref={ref}
        className="slideover"
        role="dialog"
        aria-modal="true"
        aria-labelledby="signup-title"
        inert={!open}
        onMouseDown={(e) => e.stopPropagation()}
      >
        <div className="slideover-head">
          <h2 id="signup-title">New signup</h2>
          <button type="button" className="icon-btn" aria-label="Close signup panel" onClick={onClose}>
            <X size={18} aria-hidden="true" />
          </button>
        </div>
        <form className="form" onSubmit={submit} noValidate>
          <label className="label" htmlFor="signup-name">
            Full name
          </label>
          <input
            id="signup-name"
            className="field"
            data-autofocus
            value={fullName}
            autoComplete="off"
            aria-invalid={Boolean(show("fullName"))}
            aria-describedby={show("fullName") ? "signup-name-error" : undefined}
            onChange={(e) => setFullName(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, fullName: true }))}
          />
          {show("fullName") && (
            <p id="signup-name-error" className="field-error">
              {errors.fullName}
            </p>
          )}

          <label className="label" htmlFor="signup-email">
            Email
          </label>
          <input
            id="signup-email"
            className="field"
            type="email"
            value={email}
            autoComplete="off"
            aria-invalid={Boolean(show("email"))}
            aria-describedby={show("email") ? "signup-email-error" : undefined}
            onChange={(e) => setEmail(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, email: true }))}
          />
          {show("email") && (
            <p id="signup-email-error" className="field-error">
              {errors.email}
            </p>
          )}

          <label className="label" htmlFor="signup-plan">
            Plan
          </label>
          <select
            id="signup-plan"
            className="field select-field"
            value={planId || plans[0]?.id || ""}
            onChange={(e) => setPlanId(e.target.value)}
          >
            {plans.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.duration_days} {p.duration_days === 1 ? "day" : "days"})
              </option>
            ))}
          </select>

          {apiError && (
            <p className="field-error form-error" role="alert">
              {apiError}
            </p>
          )}

          <button type="submit" className="btn btn-primary btn-big" disabled={busy || plans.length === 0}>
            {busy ? "Saving..." : "Sign up member"}
          </button>
        </form>
      </div>
    </div>
  );
}
