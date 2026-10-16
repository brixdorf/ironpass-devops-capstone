import { TriangleAlert } from "lucide-react";
import { useDialog } from "../hooks/useDialog.js";

// Modal that asks before something is deleted.
export default function ConfirmDialog({ member, onCancel, onConfirm }) {
  const open = Boolean(member);
  const ref = useDialog(open, onCancel);
  if (!open) return null;
  return (
    <div className="overlay overlay-open overlay-center" onMouseDown={onCancel}>
      <div
        ref={ref}
        className="modal"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        aria-describedby="confirm-text"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <span className="icon-tile tone-coral" aria-hidden="true">
          <TriangleAlert size={22} />
        </span>
        <h2 id="confirm-title">Delete {member.full_name}?</h2>
        <p id="confirm-text">
          This removes the member and their check-in history. It cannot be undone.
        </p>
        <div className="modal-actions">
          <button type="button" className="btn btn-outline" data-autofocus onClick={onCancel}>
            Keep member
          </button>
          <button type="button" className="btn btn-danger" onClick={onConfirm}>
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
