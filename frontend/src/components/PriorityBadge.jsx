const styles = {
  critical: "bg-red-100 text-red-800",
  high: "bg-orange-100 text-orange-800",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-gray-100 text-gray-600",
}

export default function PriorityBadge({ priority }) {
  return (
    <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${styles[priority] || ""}`}>
      {priority}
    </span>
  )
}
