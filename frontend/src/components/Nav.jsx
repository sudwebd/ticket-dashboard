import { Link, useNavigate } from "react-router-dom"

export default function Nav({ ticketId }) {
  const navigate = useNavigate()

  if (ticketId) {
    return (
      <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center justify-between">
        <button
          onClick={() => navigate(-1)}
          className="text-sm text-blue-600 hover:text-blue-800 font-medium"
        >
          &larr; Back to tickets
        </button>
        <span className="text-sm font-medium text-gray-700">{ticketId}</span>
        <div className="w-24" />
      </nav>
    )
  }

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-3 flex items-center gap-8">
      <span className="text-base font-semibold text-gray-900">SupportDesk</span>
      <Link to="/" className="text-sm text-gray-600 hover:text-gray-900 font-medium">
        Dashboard
      </Link>
    </nav>
  )
}
