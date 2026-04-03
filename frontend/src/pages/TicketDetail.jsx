import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { api } from "../api"
import Nav from "../components/Nav"
import StatusBadge from "../components/StatusBadge"
import PriorityBadge from "../components/PriorityBadge"

const CATEGORY_COLORS = {
  bug: "bg-blue-100 text-blue-800",
  feature: "bg-purple-100 text-purple-800",
  billing: "bg-orange-100 text-orange-800",
  access: "bg-teal-100 text-teal-800",
  performance: "bg-amber-100 text-amber-800",
}

const STATUSES = ["open", "in_progress", "resolved", "closed"]
const DEVELOPERS = ["Alice Chen", "Bob Patel", "Carlos Rivera", "Diana Osei", "Ethan Kim"]

function timeAgo(isoString) {
  const now = Date.now()
  const then = new Date(isoString).getTime()
  const diffMs = now - then
  const minutes = Math.floor(diffMs / 60000)
  const hours = Math.floor(diffMs / 3600000)
  const days = Math.floor(diffMs / 86400000)

  if (minutes < 60) return `${minutes} minutes ago`
  if (hours < 24) return `${hours} hours ago`
  if (days < 7) return `${days} days ago`
  return new Date(isoString).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })
}

export default function TicketDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [ticket, setTicket] = useState(null)
  const [error, setError] = useState(null)
  const [statusSaved, setStatusSaved] = useState(false)
  const [assignee, setAssignee] = useState("")
  const [assignError, setAssignError] = useState(null)

  const fetchTicket = () => {
    api.getTicket(id).then(t => {
      setTicket(t)
      setAssignee(t.assigned_to || "")
    }).catch(() => setError("Failed to load ticket. Is the server running?"))
  }

  useEffect(() => { fetchTicket() }, [id])

  const handleStatusChange = async (newStatus) => {
    await api.updateStatus(id, newStatus)
    setStatusSaved(true)
    setTimeout(() => setStatusSaved(false), 2000)
    fetchTicket()
  }

  const handleAssign = async () => {
    if (!assignee) return
    try {
      setAssignError(null)
      await api.assignTicket(id, assignee)
      fetchTicket()
    } catch {
      setAssignError("Failed to assign ticket.")
    }
  }

  const handleMarkResolved = async () => {
    await api.updateStatus(id, "resolved")
    navigate("/")
  }

  if (error) {
    return (
      <div>
        <Nav ticketId={id} />
        <div className="p-6"><p className="text-red-600">{error}</p></div>
      </div>
    )
  }

  if (!ticket) {
    return (
      <div>
        <Nav ticketId={id} />
        <div className="p-6 text-gray-500">Loading...</div>
      </div>
    )
  }

  const showResolveButton = ticket.status !== "resolved" && ticket.status !== "closed"

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav ticketId={ticket.id} />
      <div className="p-6 max-w-6xl mx-auto">
        <div className="grid grid-cols-12 gap-6">
          {/* Left panel */}
          <div className="col-span-8 space-y-5">
            <div>
              <h2 className="text-lg font-medium text-gray-900">{ticket.title}</h2>
              <div className="flex gap-2 mt-2">
                <PriorityBadge priority={ticket.priority} />
                <StatusBadge status={ticket.status} />
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium capitalize ${CATEGORY_COLORS[ticket.category] || "bg-gray-100 text-gray-700"}`}>
                  {ticket.category}
                </span>
              </div>
            </div>

            <div>
              <p className="text-xs text-gray-500 mb-1">Description</p>
              <div className="bg-gray-50 rounded p-3 text-sm text-gray-700">{ticket.description}</div>
            </div>

            <hr className="border-gray-200" />

            <div className="grid grid-cols-2 gap-y-3 text-sm">
              <div>
                <span className="text-xs text-gray-500">Created</span>
                <p className="text-gray-700">{timeAgo(ticket.created_at)} &middot; {ticket.created_by}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500">Category</span>
                <p className="text-gray-700 capitalize">{ticket.category}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500">Tags</span>
                <div className="flex gap-1 mt-0.5">
                  {ticket.tags.length > 0
                    ? ticket.tags.map(tag => (
                        <span key={tag} className="rounded-full bg-gray-100 text-gray-600 px-2 py-0.5 text-xs">{tag}</span>
                      ))
                    : <span className="text-gray-400">&mdash;</span>}
                </div>
              </div>
              <div>
                <span className="text-xs text-gray-500">Updated</span>
                <p className="text-gray-700">{timeAgo(ticket.updated_at)}</p>
              </div>
              <div>
                <span className="text-xs text-gray-500">Assigned to</span>
                <p className="text-gray-700">{ticket.assigned_to || <span className="text-gray-400">Unassigned</span>}</p>
              </div>
            </div>
          </div>

          {/* Right panel */}
          <div className="col-span-4 space-y-5">
            <div className="bg-white rounded-lg border border-gray-200 p-4 space-y-5">
              <h3 className="text-sm font-medium text-gray-900">Actions</h3>

              <div>
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Update status</span>
                  {statusSaved && <span className="text-xs text-green-600">Saved</span>}
                </div>
                <select
                  className="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
                  value={ticket.status}
                  onChange={e => handleStatusChange(e.target.value)}
                >
                  {STATUSES.map(s => (
                    <option key={s} value={s}>{s === "in_progress" ? "In Progress" : s.charAt(0).toUpperCase() + s.slice(1)}</option>
                  ))}
                </select>
              </div>

              <hr className="border-gray-200" />

              <div>
                <span className="text-xs text-gray-500">Assign to</span>
                <select
                  className="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm"
                  value={assignee}
                  onChange={e => setAssignee(e.target.value)}
                >
                  <option value="">Select developer</option>
                  {DEVELOPERS.map(d => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
                <button
                  onClick={handleAssign}
                  disabled={!assignee}
                  className="mt-2 w-full px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  Assign
                </button>
                {assignError && <p className="text-xs text-red-600 mt-1">{assignError}</p>}
              </div>

              <hr className="border-gray-200" />

              <div>
                <span className="text-xs text-gray-500">Priority</span>
                <select
                  className="mt-1 w-full border border-gray-300 rounded px-2 py-1.5 text-sm opacity-50"
                  value={ticket.priority}
                  disabled
                >
                  {["low", "medium", "high", "critical"].map(p => (
                    <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                  ))}
                </select>
                <p className="text-xs text-gray-400 mt-1">Priority update coming soon</p>
              </div>

              {showResolveButton && (
                <>
                  <hr className="border-gray-200" />
                  <button
                    onClick={handleMarkResolved}
                    className="text-sm text-blue-600 hover:text-blue-800 font-medium"
                  >
                    Mark as resolved
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
