import { useNavigate } from "react-router-dom"
import StatusBadge from "./StatusBadge"
import PriorityBadge from "./PriorityBadge"

export default function TicketTable({ tickets, total, page, totalPages, onPageChange }) {
  const navigate = useNavigate()

  if (tickets.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No tickets match the current filters.
      </div>
    )
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <p className="text-sm text-gray-500">Showing {total} tickets</p>
        {totalPages > 1 && (
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
              className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            <span className="text-sm text-gray-600">
              Page {page} of {totalPages}
            </span>
            <button
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
              className="px-3 py-1 text-sm border border-gray-300 rounded disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50">
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wide px-4 py-2">ID</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wide px-4 py-2">Title</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wide px-4 py-2">Status</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wide px-4 py-2">Priority</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wide px-4 py-2">Category</th>
              <th className="text-left text-xs font-medium text-gray-500 uppercase tracking-wide px-4 py-2">Assigned to</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map(t => (
              <tr
                key={t.id}
                onClick={() => navigate(`/tickets/${t.id}`)}
                className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
              >
                <td className="px-4 py-2 text-sm text-gray-600 font-mono">{t.id}</td>
                <td className="px-4 py-2 text-sm text-gray-900 max-w-xs truncate">{t.title}</td>
                <td className="px-4 py-2"><StatusBadge status={t.status} /></td>
                <td className="px-4 py-2"><PriorityBadge priority={t.priority} /></td>
                <td className="px-4 py-2 text-sm text-gray-600 capitalize">{t.category}</td>
                <td className="px-4 py-2 text-sm text-gray-600">{t.assigned_to || <span className="text-gray-400">&mdash;</span>}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
