import { avatarTone, initials } from "../utils.js";

export default function Avatar({ name, size = "md" }) {
  return (
    <span className={`avatar avatar-${size} tone-${avatarTone(name)}`} aria-hidden="true">
      {initials(name)}
    </span>
  );
}
