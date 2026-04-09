const BASE = "http://localhost:8000"
const API_KEY = "dashboard-key-001"

const headers = {
  "Authorization": `Bearer ${API_KEY}`,
}

const jsonHeaders = { ...headers, "Content-Type": "application/json" }

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
    headers: jsonHeaders,
    body: JSON.stringify({ assigned_to: name }),
  }).then(r => r.json()),

  updateStatus: (id, status) => fetch(`${BASE}/tickets/${id}/status?status=${status}`, {
    method: "POST",
    headers,
  }).then(r => r.json()),

  escalateTicket: (id) => fetch(`${BASE}/tickets/${id}/escalate`, {
    method: "POST",
    headers,
  }).then(r => r.json()),

  acknowledgeTicket: (id, developer) => fetch(`${BASE}/tickets/${id}/acknowledge`, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({ developer }),
  }).then(r => r.json()),

  addComment: (id, author, text) => fetch(`${BASE}/tickets/${id}/comment`, {
    method: "POST",
    headers: jsonHeaders,
    body: JSON.stringify({ author, text }),
  }).then(r => r.json()),

  reopenTicket: (id) => fetch(`${BASE}/tickets/${id}/reopen`, {
    method: "POST",
    headers,
  }).then(r => r.json()),

  getTicketHistory: (id) => fetch(`${BASE}/tickets/${id}/history`, { headers }).then(r => r.json()),
}
