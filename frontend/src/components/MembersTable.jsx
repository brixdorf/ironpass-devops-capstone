const STATUS_LABEL = {
  ACTIVE: "Active",
  EXPIRED: "Expired",
  FROZEN: "Frozen",
  CANCELLED: "Cancelled",
};

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function MembersTable({ members, loading, onRenew, onFreeze, onDelete }) {
  if (loading) return <p className="empty">Loading members...</p>;
  if (members.length === 0) return <p className="empty">No members match these filters.</p>;

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Member</th>
            <th>Plan</th>
            <th>Status</th>
            <th>Expires</th>
            <th aria-label="Actions" />
          </tr>
        </thead>
        <tbody>
          {members.map((m) => (
            <tr key={m.id}>
              <td data-label="Member">
                <span className="member-name">{m.full_name}</span>
                <span className="member-email">{m.email}</span>
              </td>
              <td data-label="Plan">{m.plan_name}</td>
              <td data-label="Status">
                <span className={`badge badge-${m.effective_status.toLowerCase()}`}>
                  {STATUS_LABEL[m.effective_status]}
                </span>
              </td>
              <td data-label="Expires" className="expires">
                {formatDate(m.expires_on)}
              </td>
              <td className="row-actions">
                <button className="link" onClick={() => onRenew(m)}>
                  Renew
                </button>
                <button className="link" onClick={() => onFreeze(m)}>
                  {m.status === "FROZEN" ? "Unfreeze" : "Freeze"}
                </button>
                <button className="link danger" onClick={() => onDelete(m)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
