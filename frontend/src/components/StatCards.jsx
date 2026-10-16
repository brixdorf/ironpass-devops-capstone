import { CalendarClock, LogIn, Snowflake, UserCheck, UserX, Users } from "lucide-react";

const CARDS = [
  { key: "total_members", label: "Total members", tone: "violet", Icon: Users },
  { key: "active_members", label: "Active now", tone: "green", Icon: UserCheck },
  { key: "check_ins_today", label: "Check-ins today", tone: "lime", Icon: LogIn },
  { key: "expiring_soon", label: "Expiring in 7 days", tone: "amber", Icon: CalendarClock },
  { key: "expired_members", label: "Expired", tone: "coral", Icon: UserX },
  { key: "frozen_members", label: "Frozen", tone: "cyan", Icon: Snowflake },
];

export default function StatCards({ stats, loading }) {
  return (
    <section className="cards" aria-label="Gym summary">
      {CARDS.map(({ key, label, tone, Icon }) => (
        <div key={key} className={`card tone-${tone}`}>
          <span className="icon-tile" aria-hidden="true">
            <Icon size={20} />
          </span>
          {loading && !stats ? (
            <span className="skeleton skeleton-number" aria-hidden="true" />
          ) : (
            <strong className="card-value">{stats ? stats[key] : "-"}</strong>
          )}
          <span className="card-label">{label}</span>
        </div>
      ))}
    </section>
  );
}
