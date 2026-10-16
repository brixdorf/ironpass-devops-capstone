import { Search } from "lucide-react";

const STATUS_FILTERS = [
  { value: "", label: "All" },
  { value: "ACTIVE", label: "Active" },
  { value: "EXPIRED", label: "Expired" },
  { value: "FROZEN", label: "Frozen" },
];

// Status filter (segmented control with counts), plan filter and a search box.
export default function Toolbar({
  counts,
  statusFilter,
  onStatus,
  plans,
  planFilter,
  onPlan,
  search,
  onSearch,
}) {
  return (
    <div className="toolbar">
      <div className="segmented" role="group" aria-label="Filter by status">
        {STATUS_FILTERS.map((f) => (
          <button
            key={f.value}
            type="button"
            className={`seg ${statusFilter === f.value ? "seg-on" : ""}`}
            aria-pressed={statusFilter === f.value}
            onClick={() => onStatus(f.value)}
          >
            {f.label}
            <span className="seg-count">{counts[f.value || "ALL"] ?? 0}</span>
          </button>
        ))}
      </div>
      <div className="toolbar-right">
        <select
          className="field select-field"
          aria-label="Filter by plan"
          value={planFilter}
          onChange={(e) => onPlan(e.target.value)}
        >
          <option value="">All plans</option>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <label className="search">
          <Search size={16} aria-hidden="true" />
          <span className="sr-only">Search members by name or email</span>
          <input
            type="search"
            placeholder="Search name or email"
            value={search}
            onChange={(e) => onSearch(e.target.value)}
          />
        </label>
      </div>
    </div>
  );
}
