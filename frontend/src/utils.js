// Small helpers shared by the components.

export const STATUS_LABEL = {
  ACTIVE: "Active",
  EXPIRED: "Expired",
  FROZEN: "Frozen",
  CANCELLED: "Cancelled",
};

// One colour per plan type. Coral is kept for "expired" only.
export const PLAN_TONE = {
  DAY_PASS: "cyan",
  MONTHLY: "lime",
  QUARTERLY: "violet",
  ANNUAL: "amber",
};

const AVATAR_TONES = ["lime", "cyan", "violet", "amber", "green"];

export function initials(name) {
  const parts = name.trim().split(/\s+/);
  const first = parts[0]?.[0] ?? "?";
  const last = parts.length > 1 ? parts[parts.length - 1][0] : "";
  return (first + last).toUpperCase();
}

// Same name always gives the same colour.
export function avatarTone(name) {
  let hash = 0;
  for (const ch of name) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  return AVATAR_TONES[hash % AVATAR_TONES.length];
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

// 2026-09-26 becomes "26 Sep 2026" in every browser.
export function formatDate(value) {
  const [year, month, day] = value.split("-");
  return `${day} ${MONTHS[Number(month) - 1]} ${year}`;
}

export function timeAgo(iso) {
  const minutes = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (minutes < 1) return "just now";
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  return `${Math.round(hours / 24)} d ago`;
}
