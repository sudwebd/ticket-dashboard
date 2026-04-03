export default function StatCard({ label, value }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-2xl font-medium text-gray-900 mt-1">{value}</p>
    </div>
  )
}
