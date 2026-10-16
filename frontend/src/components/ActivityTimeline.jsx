import { Activity, LogIn, UserPlus } from "lucide-react";
import { timeAgo } from "../utils.js";

export default function ActivityTimeline({ activity, loading }) {
  return (
    <section className="panel" aria-labelledby="activity-title">
      <div className="panel-head">
        <span className="icon-tile tone-cyan" aria-hidden="true">
          <Activity size={20} />
        </span>
        <h2 id="activity-title">Recent activity</h2>
      </div>
      {loading ? (
        <div className="skeleton-list" aria-hidden="true">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="skeleton-row">
              <span className="skeleton skeleton-circle" />
              <span className="skeleton skeleton-line" />
            </div>
          ))}
        </div>
      ) : activity.length === 0 ? (
        <p className="muted-text">Nothing has happened yet.</p>
      ) : (
        <ol className="timeline">
          {activity.map((item) => {
            const checkin = item.type === "CHECKIN";
            return (
              <li key={`${item.type}-${item.member_id}-${item.at}`}>
                <span className={`timeline-dot tone-${checkin ? "lime" : "violet"}`} aria-hidden="true">
                  {checkin ? <LogIn size={14} /> : <UserPlus size={14} />}
                </span>
                <div className="timeline-body">
                  <span className="timeline-kind">{checkin ? "Check-in" : "Signup"}</span>
                  <span className="timeline-text">{item.message}</span>
                </div>
                <time className="timeline-time mono" dateTime={item.at}>
                  {timeAgo(item.at)}
                </time>
              </li>
            );
          })}
        </ol>
      )}
    </section>
  );
}
