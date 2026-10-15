import { useState } from "react";

export default function SignupForm({ plans, onCreate }) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [planId, setPlanId] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    const ok = await onCreate({
      full_name: fullName,
      email,
      plan_id: Number(planId || plans[0]?.id),
    });
    setBusy(false);
    if (ok) {
      setFullName("");
      setEmail("");
    }
  }

  return (
    <form className="panel form" onSubmit={submit}>
      <h2>New signup</h2>
      <label>
        Full name
        <input value={fullName} onChange={(e) => setFullName(e.target.value)} required minLength={2} />
      </label>
      <label>
        Email
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </label>
      <label>
        Plan
        <select value={planId || plans[0]?.id || ""} onChange={(e) => setPlanId(e.target.value)}>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name} ({p.duration_days} days)
            </option>
          ))}
        </select>
      </label>
      <button className="primary" disabled={busy || plans.length === 0}>
        {busy ? "Saving..." : "Sign up member"}
      </button>
    </form>
  );
}
