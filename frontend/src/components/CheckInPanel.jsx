import { useState } from "react";

function timeAgo(iso) {
  const minutes = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  return `${Math.round(hours / 24)} d ago`;
}

export default function CheckInPanel({ members, recent, onCheckIn }) {
  const [memberId, setMemberId] = useState("");
  const [busy, setBusy] = useState(false);
  const selected = memberId || members[0]?.id || "";

  async function submit(event) {
    event.preventDefault();
    if (!selected) return;
    setBusy(true);
    await onCheckIn(Number(selected));
    setBusy(false);
  }

  return (
    <div className="panel">
      <form className="form" onSubmit={submit}>
        <h2>Front desk check-in</h2>
        <label>
          Member
          <select value={selected} onChange={(e) => setMemberId(e.target.value)}>
            {members.map((m) => (
              <option key={m.id} value={m.id}>
                {m.full_name}
              </option>
            ))}
          </select>
        </label>
        <button className="primary" disabled={busy || !selected}>
          Check in
        </button>
      </form>
      <h3>Recent visits</h3>
      {recent.length === 0 ? (
        <p className="empty small">No visits yet.</p>
      ) : (
        <ul className="visits">
          {recent.map((v) => (
            <li key={v.id}>
              <span>{v.member_name}</span>
              <span className="muted">{timeAgo(v.checked_in_at)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
