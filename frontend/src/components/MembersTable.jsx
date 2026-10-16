import { Pause, Play, RefreshCw, SearchX, Trash2 } from "lucide-react";
import Avatar from "./Avatar.jsx";
import { PLAN_TONE, STATUS_LABEL, formatDate } from "../utils.js";

function IconButton({ label, tone, onClick, children }) {
  return (
    <button
      type="button"
      className={`icon-btn ${tone ? `icon-btn-${tone}` : ""}`}
      aria-label={label}
      data-tip={label}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function SkeletonRows() {
  return (
    <div className="skeleton-list" aria-hidden="true">
      {[0, 1, 2, 3, 4].map((i) => (
        <div key={i} className="skeleton-row">
          <span className="skeleton skeleton-circle" />
          <span className="skeleton skeleton-line" />
          <span className="skeleton skeleton-pill" />
        </div>
      ))}
    </div>
  );
}

export default function MembersTable({ members, loading, onRenew, onFreeze, onDelete, onReset }) {
  if (loading) return <SkeletonRows />;
  if (members.length === 0) {
    return (
      <div className="empty-state">
        <span className="icon-tile tone-violet" aria-hidden="true">
          <SearchX size={22} />
        </span>
        <strong>No members match</strong>
        <p>Try another filter or clear the search box.</p>
        <button type="button" className="btn btn-outline" onClick={onReset}>
          Clear filters
        </button>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th scope="col">Member</th>
            <th scope="col">Plan</th>
            <th scope="col">Status</th>
            <th scope="col">Expires</th>
            <th scope="col">
              <span className="sr-only">Actions</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {members.map((m) => {
            const state = m.effective_status;
            return (
              <tr key={m.id}>
                <td data-label="Member">
                  <div className="person">
                    <Avatar name={m.full_name} />
                    <div className="person-text">
                      <span className="member-name">{m.full_name}</span>
                      <span className="member-email">{m.email}</span>
                    </div>
                  </div>
                </td>
                <td data-label="Plan">
                  <span className={`badge tone-${PLAN_TONE[m.plan_type] || "violet"}`}>
                    {m.plan_name}
                  </span>
                </td>
                <td data-label="Status">
                  <span className={`pill pill-${state.toLowerCase()}`}>
                    <span className="dot" aria-hidden="true" />
                    {STATUS_LABEL[state]}
                  </span>
                </td>
                <td data-label="Expires" className="mono">
                  {formatDate(m.expires_on)}
                </td>
                <td className="row-actions">
                  <IconButton label={`Renew ${m.full_name}`} tone="lime" onClick={() => onRenew(m)}>
                    <RefreshCw size={16} aria-hidden="true" />
                  </IconButton>
                  <IconButton
                    label={`${m.status === "FROZEN" ? "Unfreeze" : "Freeze"} ${m.full_name}`}
                    tone="cyan"
                    onClick={() => onFreeze(m)}
                  >
                    {m.status === "FROZEN" ? (
                      <Play size={16} aria-hidden="true" />
                    ) : (
                      <Pause size={16} aria-hidden="true" />
                    )}
                  </IconButton>
                  <IconButton label={`Delete ${m.full_name}`} tone="coral" onClick={() => onDelete(m)}>
                    <Trash2 size={16} aria-hidden="true" />
                  </IconButton>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
