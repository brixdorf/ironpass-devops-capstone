const CARDS = [
  { key: "total_members", label: "Total members", tone: "dark" },
  { key: "active_members", label: "Active now", tone: "good" },
  { key: "check_ins_today", label: "Check-ins today", tone: "accent" },
  { key: "expiring_soon", label: "Expiring in 7 days", tone: "warn" },
  { key: "expired_members", label: "Expired", tone: "bad" },
  { key: "frozen_members", label: "Frozen", tone: "muted" },
];

export default function StatCards({ stats }) {
  return (
    <section className="cards" aria-label="Gym summary">
      {CARDS.map((card) => (
        <div key={card.key} className={`card card-${card.tone}`}>
          <span className="card-label">{card.label}</span>
          <strong className="card-value">{stats ? stats[card.key] : "-"}</strong>
        </div>
      ))}
    </section>
  );
}
