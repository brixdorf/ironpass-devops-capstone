import { useState } from "react";
import { CircleCheck, DoorOpen, OctagonX } from "lucide-react";
import Avatar from "./Avatar.jsx";
import { PLAN_TONE, STATUS_LABEL, formatDate } from "../utils.js";

function refusalText(member) {
  if (member.effective_status === "EXPIRED") {
    return `The ${member.plan_name} plan ended on ${formatDate(member.expires_on)}. Renew it to let them in.`;
  }
  if (member.effective_status === "FROZEN") {
    return "This membership is frozen. Unfreeze it to let them in.";
  }
  return "This membership is not active.";
}

export default function CheckInPanel({ members, onCheckIn }) {
  const [memberId, setMemberId] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const selected = memberId || String(members[0]?.id ?? "");
  const member = members.find((m) => String(m.id) === selected);

  async function submit(event) {
    event.preventDefault();
    if (!member) return;
    setBusy(true);
    const outcome = await onCheckIn(member.id);
    setBusy(false);
    setResult({
      ok: outcome.ok,
      name: member.full_name,
      detail: outcome.ok ? "Enjoy the session." : refusalText(member),
      api: outcome.error,
      time: new Date().toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" }),
    });
  }

  return (
    <section className="panel" aria-labelledby="checkin-title">
      <div className="panel-head">
        <span className="icon-tile tone-lime" aria-hidden="true">
          <DoorOpen size={20} />
        </span>
        <h2 id="checkin-title">Front desk check-in</h2>
      </div>

      <form className="form" onSubmit={submit}>
        <label className="label" htmlFor="checkin-member">
          Member
        </label>
        <select
          id="checkin-member"
          className="field select-field"
          value={selected}
          onChange={(e) => {
            setMemberId(e.target.value);
            setResult(null);
          }}
        >
          {members.map((m) => (
            <option key={m.id} value={m.id}>
              {m.full_name}
            </option>
          ))}
        </select>

        {member && (
          <div className="preview">
            <Avatar name={member.full_name} />
            <div className="person-text">
              <span className="member-name">{member.full_name}</span>
              <span className="member-email">
                <span className={`inline-tone tone-${PLAN_TONE[member.plan_type] || "violet"}`}>
                  {member.plan_name}
                </span>
                {" · "}
                {STATUS_LABEL[member.effective_status]}
              </span>
            </div>
          </div>
        )}

        <button type="submit" className="btn btn-primary btn-big" disabled={busy || !member}>
          {busy ? "Checking..." : "Check in"}
        </button>
      </form>

      <div className="result-slot" aria-live="assertive" aria-atomic="true">
        {result && result.ok && (
          <div className="result result-ok">
            <CircleCheck size={28} aria-hidden="true" />
            <div>
              <strong>Welcome in, {result.name}</strong>
              <p>
                Checked in at <span className="mono">{result.time}</span>. {result.detail}
              </p>
            </div>
          </div>
        )}
        {result && !result.ok && (
          <div className="result result-refused">
            <OctagonX size={28} aria-hidden="true" />
            <div>
              <strong>Check-in refused for {result.name}</strong>
              <p>{result.detail}</p>
              {result.api && <p className="api-line mono">{result.api}</p>}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
