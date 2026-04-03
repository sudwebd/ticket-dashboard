import { useState, useEffect } from "react"
import { api } from "../api"
import Nav from "../components/Nav"
import StatCard from "../components/StatCard"
import CategoryChart from "../components/CategoryChart"
import DeveloperChart from "../components/DeveloperChart"
import FilterBar from "../components/FilterBar"
import TicketTable from "../components/TicketTable"

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [ticketData, setTicketData] = useState(null)
  const [filters, setFilters] = useState({ status: "", priority: "", category: "", assigned_to: "", unassigned: null })
  const [page, setPage] = useState(1)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getSummary().then(setSummary).catch(() => setError("Failed to load data. Is the server running?"))
  }, [])

  useEffect(() => {
    setError(null)
    const params = { page, page_size: 20 }
    if (filters.status) params.status = filters.status
    if (filters.priority) params.priority = filters.priority
    if (filters.category) params.category = filters.category
    if (filters.assigned_to) params.assigned_to = filters.assigned_to
    if (filters.unassigned) params.unassigned = true

    api.getTicketsPage(params).then(setTicketData).catch(() => setError("Failed to load data. Is the server running?"))
  }, [filters, page])

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters)
    setPage(1)
  }

  const avgAge = ticketData?.tickets?.length
    ? Math.round(
        ticketData.tickets.reduce((sum, t) => {
          const days = (Date.now() - new Date(t.created_at).getTime()) / (1000 * 60 * 60 * 24)
          return sum + days
        }, 0) / ticketData.tickets.length
      )
    : 0

  if (error) {
    return (
      <div>
        <Nav />
        <div className="p-6">
          <p className="text-red-600">{error}</p>
        </div>
      </div>
    )
  }

  if (!summary || !ticketData) {
    return (
      <div>
        <Nav />
        <div className="p-6 text-gray-500">Loading...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Nav />
      <div className="p-6 max-w-7xl mx-auto space-y-6">
        <div className="grid grid-cols-4 gap-4">
          <StatCard label="Total open" value={summary.by_status.open || 0} />
          <StatCard label="Critical" value={summary.by_priority.critical || 0} />
          <StatCard label="Unassigned" value={summary.unassigned} />
          <StatCard label="Avg age (days)" value={avgAge} />
        </div>

        <div className="grid grid-cols-12 gap-4">
          <div className="col-span-5">
            <CategoryChart byCategory={summary.by_category} />
          </div>
          <div className="col-span-7">
            <DeveloperChart developerLoad={summary.developer_load} />
          </div>
        </div>

        <FilterBar filters={filters} setFilters={handleFilterChange} />

        <TicketTable
          tickets={ticketData.tickets}
          total={ticketData.total}
          page={ticketData.page}
          totalPages={ticketData.total_pages}
          onPageChange={setPage}
        />
      </div>
    </div>
  )
}
