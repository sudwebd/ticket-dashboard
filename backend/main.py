"""FastAPI backend for the support ticket dashboard."""

import json
import math
from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

app = FastAPI(title="Support Ticket Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_tickets: list[dict] = []

# --- Dummy Auth ---

API_KEYS = {
    "dashboard-key-001": {"name": "Frontend Dashboard", "role": "admin"},
    "calyb-key-002": {"name": "Calyb Connector", "role": "reader"},
    "agent-key-003": {"name": "Data View Agent", "role": "reader"},
}

_bearer_scheme = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme)):
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return API_KEYS[token]


@app.on_event("startup")
def load_tickets():
    global _tickets
    with open("tickets.json") as f:
        _tickets = json.load(f)
    print(f"Loaded {len(_tickets)} tickets")


# --- Models ---

class Ticket(BaseModel):
    id: str
    title: str
    description: str
    status: Literal["open", "in_progress", "resolved", "closed"]
    priority: Literal["low", "medium", "high", "critical"]
    category: Literal["bug", "feature", "billing", "access", "performance"]
    assigned_to: Optional[str]
    created_at: str
    updated_at: str
    created_by: str
    tags: list[str]


class BulkResponse(BaseModel):
    total: int
    tickets: list[Ticket]


class PagedResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    tickets: list[Ticket]


class AssignRequest(BaseModel):
    assigned_to: str


class SummaryResponse(BaseModel):
    total_tickets: int
    by_status: dict[str, int]
    by_priority: dict[str, int]
    by_category: dict[str, int]
    unassigned: int
    developer_load: list[dict]


# --- Helper ---

def _filter_tickets(
    tickets: list[dict],
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[str] = None,
    unassigned: Optional[bool] = None,
) -> list[dict]:
    result = tickets
    if status:
        result = [t for t in result if t["status"] == status]
    if priority:
        result = [t for t in result if t["priority"] == priority]
    if category:
        result = [t for t in result if t["category"] == category]
    if assigned_to:
        result = [t for t in result if t["assigned_to"] == assigned_to]
    if unassigned:
        result = [t for t in result if t["assigned_to"] is None]
    return result


# --- Endpoints ---

@app.get("/tickets/page", response_model=PagedResponse)
def get_tickets_page(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[str] = None,
    unassigned: Optional[bool] = None,
    _auth: dict = Depends(verify_token),
):
    filtered = _filter_tickets(_tickets, status, priority, category, assigned_to, unassigned)
    total = len(filtered)
    total_pages = max(1, math.ceil(total / page_size))
    start = (page - 1) * page_size
    end = start + page_size
    return PagedResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        tickets=filtered[start:end],
    )


@app.get("/tickets", response_model=BulkResponse)
def get_tickets_bulk(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assigned_to: Optional[str] = None,
    unassigned: Optional[bool] = None,
    created_after: Optional[str] = None,
    created_before: Optional[str] = None,
    tag: Optional[str] = None,
    _auth: dict = Depends(verify_token),
):
    result = _filter_tickets(_tickets, status, priority, category, assigned_to, unassigned)
    if created_after:
        dt = datetime.fromisoformat(created_after)
        result = [t for t in result if datetime.fromisoformat(t["created_at"]) >= dt]
    if created_before:
        dt = datetime.fromisoformat(created_before)
        result = [t for t in result if datetime.fromisoformat(t["created_at"]) <= dt]
    if tag:
        result = [t for t in result if tag in t["tags"]]
    return BulkResponse(total=len(result), tickets=result)


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str, _auth: dict = Depends(verify_token)):
    for t in _tickets:
        if t["id"] == ticket_id:
            return t
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.post("/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id: str, req: AssignRequest, _auth: dict = Depends(verify_token)):
    for t in _tickets:
        if t["id"] == ticket_id:
            t["assigned_to"] = req.assigned_to
            t["updated_at"] = datetime.now(timezone.utc).isoformat()
            return {
                "id": t["id"],
                "assigned_to": t["assigned_to"],
                "updated_at": t["updated_at"],
                "message": f"Ticket {ticket_id} assigned to {req.assigned_to}",
            }
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.post("/tickets/{ticket_id}/status")
def update_status(
    ticket_id: str,
    status: Literal["open", "in_progress", "resolved", "closed"] = Query(...),
    _auth: dict = Depends(verify_token),
):
    for t in _tickets:
        if t["id"] == ticket_id:
            t["status"] = status
            t["updated_at"] = datetime.now(timezone.utc).isoformat()
            return {
                "id": t["id"],
                "status": t["status"],
                "updated_at": t["updated_at"],
            }
    raise HTTPException(status_code=404, detail="Ticket not found")


@app.get("/summary", response_model=SummaryResponse)
def get_summary(_auth: dict = Depends(verify_token)):
    from collections import Counter

    by_status = Counter(t["status"] for t in _tickets)
    by_priority = Counter(t["priority"] for t in _tickets)
    by_category = Counter(t["category"] for t in _tickets)
    unassigned = sum(1 for t in _tickets if t["assigned_to"] is None)

    dev_open: dict[str, int] = {}
    for t in _tickets:
        if t["assigned_to"] and t["status"] == "open":
            dev_open[t["assigned_to"]] = dev_open.get(t["assigned_to"], 0) + 1
    developer_load = sorted(
        [{"developer": d, "open_tickets": c} for d, c in dev_open.items()],
        key=lambda x: x["open_tickets"],
    )

    return SummaryResponse(
        total_tickets=len(_tickets),
        by_status=dict(by_status),
        by_priority=dict(by_priority),
        by_category=dict(by_category),
        unassigned=unassigned,
        developer_load=developer_load,
    )


@app.get("/health")
def health():
    return {"status": "ok", "tickets_loaded": len(_tickets)}
