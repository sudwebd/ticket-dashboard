const styles = {
  open: "bg-green-100 text-green-800",
  in_progress: "bg-blue-100 text-blue-800",
  resolved: "bg-gray-100 text-gray-700",
  closed: "bg-gray-50 text-gray-500",
}

const labels = {
  open: "Open",
  in_progress: "In Progress",
  resolved: "Resolved",
  closed: "Closed",
}

export default function StatusBadge({ status }) {
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${styles[status] || ""}`}>
      {labels[status] || status}
    </span>
  )
}
