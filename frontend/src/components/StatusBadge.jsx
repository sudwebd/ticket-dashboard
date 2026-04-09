const styles = {
  open: "bg-green-100 text-green-800",
  acknowledged: "bg-cyan-100 text-cyan-800",
  in_progress: "bg-blue-100 text-blue-800",
  waiting_on_info: "bg-yellow-100 text-yellow-800",
  resolved: "bg-gray-100 text-gray-700",
  closed: "bg-gray-50 text-gray-500",
}

const labels = {
  open: "Open",
  acknowledged: "Acknowledged",
  in_progress: "In Progress",
  waiting_on_info: "Waiting on Info",
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
