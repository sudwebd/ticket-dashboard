const BASE = "http://localhost:8000"
const API_KEY = "dashboard-key-001"

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
}

export const api = {
  getTicketsPage: (params = {}) => {
    const qs = new URLSearchParams(
      Object.fromEntries(Object.entries(params).filter(([_, v]) => v !== "" && v != null))
    ).toString()
    return fetch(`${BASE}/tickets/page${qs ? "?" + qs : ""}`, { headers }).then(r => r.json())
  },

  getTicket: (id) => fetch(`${BASE}/tickets/${id}`, { headers }).then(r => r.json()),

  getSummary: () => fetch(`${BASE}/summary`, { headers }).then(r => r.json()),

  assignTicket: (id, name) => fetch(`${BASE}/tickets/${id}/assign`, {
    method: "POST",
    headers: { ...headers, "Content-Type": "application/json" },
    body: JSON.stringify({ assigned_to: name }),
  }).then(r => r.json()),

  updateStatus: (id, status) => fetch(`${BASE}/tickets/${id}/status?status=${status}`, {
    method: "POST",
    headers,
  }).then(r => r.json()),
}
