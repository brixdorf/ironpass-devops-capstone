import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Users } from "lucide-react";
import { api } from "./api.js";
import Header from "./components/Header.jsx";
import StatCards from "./components/StatCards.jsx";
import Toolbar from "./components/Toolbar.jsx";
import MembersTable from "./components/MembersTable.jsx";
import CheckInPanel from "./components/CheckInPanel.jsx";
import ActivityTimeline from "./components/ActivityTimeline.jsx";
import SignupPanel from "./components/SignupPanel.jsx";
import ConfirmDialog from "./components/ConfirmDialog.jsx";
import Toasts from "./components/Toasts.jsx";
import ErrorState from "./components/ErrorState.jsx";

export default function App() {
  const [stats, setStats] = useState(null);
  const [plans, setPlans] = useState([]);
  const [members, setMembers] = useState([]);
  const [allMembers, setAllMembers] = useState([]);
  const [activity, setActivity] = useState([]);
  const [planFilter, setPlanFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toasts, setToasts] = useState([]);
  const [signupOpen, setSignupOpen] = useState(false);
  const [toDelete, setToDelete] = useState(null);
  const toastId = useRef(0);

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
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [planFilter, statusFilter]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  function flash(kind, text) {
    const id = ++toastId.current;
    setToasts((list) => [...list, { id, kind, text }]);
    setTimeout(() => setToasts((list) => list.filter((t) => t.id !== id)), 4000);
  }

  // Runs an API call, shows a toast and reloads the data. Returns what happened.
  async function attempt(action, successText) {
    try {
      const data = await action();
      flash("ok", successText);
      await refresh();
      return { ok: true, data };
    } catch (err) {
      flash("error", err.message);
      return { ok: false, error: err.message };
    }
  }

  function retry() {
    setLoading(true);
    refresh();
  }

  function resetFilters() {
    setStatusFilter("");
    setPlanFilter("");
    setSearch("");
  }

  const counts = useMemo(() => {
    const result = { ALL: allMembers.length, ACTIVE: 0, EXPIRED: 0, FROZEN: 0 };
    allMembers.forEach((m) => {
      if (result[m.effective_status] !== undefined) result[m.effective_status] += 1;
    });
    return result;
  }, [allMembers]);

  const visible = useMemo(() => {
    const needle = search.trim().toLowerCase();
    if (!needle) return members;
    return members.filter(
      (m) => m.full_name.toLowerCase().includes(needle) || m.email.toLowerCase().includes(needle)
    );
  }, [members, search]);

  const apiDown = Boolean(error) && !stats;

  return (
    <div className="shell">
      <Header onSignup={() => setSignupOpen(true)} />

      <main className="content">
        {apiDown ? (
          <ErrorState message={error} onRetry={retry} />
        ) : (
          <>
            {error && <ErrorState compact message={error} onRetry={retry} />}
            <StatCards stats={stats} loading={loading} />

            <div className="layout">
              <section className="panel members" aria-labelledby="members-title">
                <div className="panel-head">
                  <span className="icon-tile tone-violet" aria-hidden="true">
                    <Users size={20} />
                  </span>
                  <h2 id="members-title">Members</h2>
                </div>
                <Toolbar
                  counts={counts}
                  statusFilter={statusFilter}
                  onStatus={setStatusFilter}
                  plans={plans}
                  planFilter={planFilter}
                  onPlan={setPlanFilter}
                  search={search}
                  onSearch={setSearch}
                />
                <MembersTable
                  members={visible}
                  loading={loading}
                  onReset={resetFilters}
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
                  onDelete={setToDelete}
                />
              </section>

              <div className="side">
                <CheckInPanel
                  members={allMembers}
                  onCheckIn={(id) => attempt(() => api.checkIn(id), "Check-in accepted")}
                />
                <ActivityTimeline activity={activity} loading={loading} />
              </div>
            </div>
          </>
        )}
      </main>

      <SignupPanel
        open={signupOpen}
        plans={plans}
        onClose={() => setSignupOpen(false)}
        onCreate={async (body) => {
          const outcome = await attempt(() => api.createMember(body), "Member signed up");
          if (outcome.ok) setSignupOpen(false);
          return outcome;
        }}
      />

      <ConfirmDialog
        member={toDelete}
        onCancel={() => setToDelete(null)}
        onConfirm={async () => {
          const m = toDelete;
          setToDelete(null);
          await attempt(() => api.deleteMember(m.id), `${m.full_name} deleted`);
        }}
      />

      <Toasts toasts={toasts} />
    </div>
  );
}
