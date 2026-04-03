export default function DeveloperChart({ developerLoad }) {
  if (!developerLoad || developerLoad.length === 0) return null

  const max = Math.max(...developerLoad.map(d => d.open_tickets), 1)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm text-gray-500 mb-3">Developer Load (Open Tickets)</h3>
      <div className="space-y-2">
        {developerLoad.map(d => (
          <div key={d.developer} className="flex items-center gap-3">
            <span className="text-sm w-28 text-gray-700 truncate">{d.developer}</span>
            <div className="flex-1 h-5 bg-gray-100 rounded overflow-hidden">
              <div
                className="h-full rounded bg-blue-500"
                style={{ width: `${(d.open_tickets / max) * 100}%` }}
              />
            </div>
            <span className="text-sm text-gray-600 w-8 text-right">{d.open_tickets}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
