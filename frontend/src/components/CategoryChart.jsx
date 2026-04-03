const COLORS = {
  bug: "#378ADD",
  feature: "#7F77DD",
  billing: "#D85A30",
  access: "#1D9E75",
  performance: "#EF9F27",
}

export default function CategoryChart({ byCategory }) {
  if (!byCategory) return null

  const entries = Object.entries(byCategory)
  const max = Math.max(...entries.map(([, v]) => v), 1)

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <h3 className="text-sm text-gray-500 mb-3">Tickets by Category</h3>
      <div className="space-y-2">
        {entries.map(([cat, count]) => (
          <div key={cat} className="flex items-center gap-3">
            <span className="text-sm w-24 text-gray-700 capitalize">{cat}</span>
            <div className="flex-1 h-5 bg-gray-100 rounded overflow-hidden">
              <div
                className="h-full rounded"
                style={{
                  width: `${(count / max) * 100}%`,
                  backgroundColor: COLORS[cat] || "#999",
                }}
              />
            </div>
            <span className="text-sm text-gray-600 w-8 text-right">{count}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
