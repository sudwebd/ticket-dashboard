const STATUSES = ["open", "acknowledged", "in_progress", "waiting_on_info", "resolved", "closed"]
const PRIORITIES = ["low", "medium", "high", "critical"]
const CATEGORIES = ["bug", "feature", "billing", "access", "performance"]
const DEVELOPERS = ["Alice Chen", "Bob Patel", "Carlos Rivera", "Diana Osei", "Ethan Kim"]

export default function FilterBar({ filters, setFilters }) {
  const update = (key, value) => {
    if (key === "assigned_to" && value === "__unassigned__") {
      setFilters(prev => ({ ...prev, assigned_to: "", unassigned: true }))
    } else if (key === "assigned_to") {
      setFilters(prev => ({ ...prev, assigned_to: value, unassigned: null }))
    } else {
      setFilters(prev => ({ ...prev, [key]: value }))
    }
  }

  const clear = () => setFilters({ status: "", priority: "", category: "", assigned_to: "", unassigned: null })

  const assignedValue = filters.unassigned ? "__unassigned__" : (filters.assigned_to || "")

  return (
    <div className="flex items-center gap-3 flex-wrap">
      <select
        className="border border-gray-300 rounded px-2 py-1.5 text-sm"
        value={filters.status || ""}
        onChange={e => update("status", e.target.value)}
      >
        <option value="">All statuses</option>
        {STATUSES.map(s => {
          const label = { in_progress: "In Progress", waiting_on_info: "Waiting on Info" }[s] || s.charAt(0).toUpperCase() + s.slice(1)
          return <option key={s} value={s}>{label}</option>
        })}
      </select>

      <select
        className="border border-gray-300 rounded px-2 py-1.5 text-sm"
        value={filters.priority || ""}
        onChange={e => update("priority", e.target.value)}
      >
        <option value="">All priorities</option>
        {PRIORITIES.map(p => (
          <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
        ))}
      </select>

      <select
        className="border border-gray-300 rounded px-2 py-1.5 text-sm"
        value={filters.category || ""}
        onChange={e => update("category", e.target.value)}
      >
        <option value="">All categories</option>
        {CATEGORIES.map(c => (
          <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
        ))}
      </select>

      <select
        className="border border-gray-300 rounded px-2 py-1.5 text-sm"
        value={assignedValue}
        onChange={e => update("assigned_to", e.target.value)}
      >
        <option value="">All assignees</option>
        <option value="__unassigned__">Unassigned</option>
        {DEVELOPERS.map(d => (
          <option key={d} value={d}>{d}</option>
        ))}
      </select>

      <button
        onClick={clear}
        className="text-sm text-gray-500 hover:text-gray-700 px-2 py-1.5"
      >
        Clear filters
      </button>
    </div>
  )
}
