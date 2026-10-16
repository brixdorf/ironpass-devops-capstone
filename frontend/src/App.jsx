import { useCallback, useEffect, useState } from "react";
import { api } from "./api.js";
import StatCards from "./components/StatCards.jsx";
import MembersTable from "./components/MembersTable.jsx";
import SignupForm from "./components/SignupForm.jsx";
import CheckInPanel from "./components/CheckInPanel.jsx";

const STATUS_FILTERS = [
  { value: "", label: "All" },
  { value: "ACTIVE", label: "Active" },
  { value: "EXPIRED", label: "Expired" },
  { value: "FROZEN", label: "Frozen" },
];

export default function App() {
  const [stats, setStats] = useState(null);
  const [plans, setPlans] = useState([]);
  const [members, setMembers] = useState([]);
  const [allMembers, setAllMembers] = useState([]);
  const [activity, setActivity] = useState([]);
  const [planFilter, setPlanFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const [s, p, list, everyone, a] = await Promise.all([
        api.stats(),
        api.plans(),
        api.members({ plan_id: planFilter, status: statusFilter }),
        api.members(),
        api.activity(),
      ]);
      setStats(s);
      setPlans(p);
      setMembers(list);
      setAllMembers(everyone);
      setActivity(a);
      setError("");
    } catch (err) {
      setError("Could not reach the IronPass API. " + err.message);
    } finally {
      setLoading(false);
    }
  }, [planFilter, statusFilter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function flash(kind, text) {
    setNotice({ kind, text });
    setTimeout(() => setNotice(null), 4000);
  }

  async function attempt(action, successText) {
    try {
      await action();
      flash("ok", successText);
      await refresh();
      return true;
    } catch (err) {
      flash("error", err.message);
      return false;
    }
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true" />
          <span>
            Iron<b>Pass</b>
          </span>
        </div>
        <span className="tagline">Gym membership desk</span>
      </header>

      <main className="content">
        {error && <div className="banner error">{error}</div>}
        {notice && <div className={`banner ${notice.kind}`}>{notice.text}</div>}

        <StatCards stats={stats} />

        <div className="layout">
          <section className="panel members">
            <div className="panel-head">
              <h2>Members</h2>
              <div className="filters">
                <div className="chips" role="group" aria-label="Filter by status">
                  {STATUS_FILTERS.map((f) => (
                    <button
                      key={f.value}
                      className={`chip ${statusFilter === f.value ? "chip-on" : ""}`}
                      onClick={() => setStatusFilter(f.value)}
                    >
                      {f.label}
                    </button>
                  ))}
                </div>
                <select
                  aria-label="Filter by plan"
                  value={planFilter}
                  onChange={(e) => setPlanFilter(e.target.value)}
                >
                  <option value="">All plans</option>
                  {plans.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <MembersTable
              members={members}
              loading={loading}
              onRenew={(m) => attempt(() => api.renewMember(m.id), `${m.full_name} renewed`)}
              onFreeze={(m) =>
                attempt(
                  () =>
                    api.updateMember(m.id, {
                      status: m.status === "FROZEN" ? "ACTIVE" : "FROZEN",
                    }),
                  `${m.full_name} updated`
                )
              }
              onDelete={(m) => {
                if (window.confirm(`Delete ${m.full_name}?`)) {
                  attempt(() => api.deleteMember(m.id), `${m.full_name} deleted`);
                }
              }}
            />
          </section>

          <aside className="side">
            <CheckInPanel
              members={allMembers}
              activity={activity}
              onCheckIn={(id) => attempt(() => api.checkIn(id), "Check-in accepted")}
            />
            <SignupForm
              plans={plans}
              onCreate={(body) => attempt(() => api.createMember(body), "Member signed up")}
            />
          </aside>
        </div>
      </main>
    </div>
  );
}
