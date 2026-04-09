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

# --- Developer data ---

DEVELOPERS_DATA = {
    "Alice Chen": {"specialisations": ["backend", "auth"]},
    "Bob Patel": {"specialisations": ["frontend", "ui"]},
    "Carlos Rivera": {"specialisations": ["backend", "performance"]},
    "Diana Osei": {"specialisations": ["billing", "data"]},
    "Ethan Kim": {"specialisations": ["frontend", "access"]},
}

# --- Dummy Auth ---

API_KEYS = {
    "dashboard-key-001": {"name": "Frontend Dashboard", "role": "admin"},
    "calyb-key-002": {"name": "Calyb Connector", "role": "reader"},
    "agent-key-003": {"name": "Data View Agent", "role": "agent"},
}

_bearer_scheme = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme)):
    token = credentials.credentials
    if token not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return {**API_KEYS[token], "key": token}


def require_write(auth: dict):
    """Raise 403 if the caller does not have write access."""
    if auth["role"] == "reader":
        raise HTTPException(status_code=403, detail="Insufficient permissions")


# --- State machine ---

VALID_STATUSES = {"open", "acknowledged", "in_progress", "waiting_on_info", "resolved", "closed"}

STATUS_TRANSITIONS: dict[str, set[str]] = {
    "open": {"acknowledged", "in_progress", "waiting_on_info"},
    "acknowledged": {"in_progress", "waiting_on_info"},
    "in_progress": {"resolved", "waiting_on_info"},
    "waiting_on_info": set(),  # only via reopen -> open
    "resolved": {"closed"},    # only via reopen -> open
    "closed": set(),           # only via reopen -> open
}

PRIORITY_LEVELS = ["low", "medium", "high", "critical"]


def _error_400(reason: str, detail: str):
    raise HTTPException(
        status_code=400,
        detail={"error": "precondition_failed", "reason": reason, "detail": detail},
    )


def _find_ticket(ticket_id: str) -> dict:
    for t in _tickets:
        if t["id"] == ticket_id:
            return t
    raise HTTPException(status_code=404, detail="Ticket not found")


def _append_history(ticket: dict, action: str, actor: str = "system",
                    from_status: str | None = None, to_status: str | None = None,
                    notes: str | None = None):
    ticket["history"].append({
        "action": action,
        "actor": actor,
        "from_status": from_status,
        "to_status": to_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "notes": notes,
    })


def _touch(ticket: dict):
    ticket["updated_at"] = datetime.now(timezone.utc).isoformat()


@app.on_event("startup")
def load_tickets():
    global _tickets
    with open("tickets.json") as f:
        _tickets = json.load(f)
    # Ensure all tickets have comments and history fields
    for t in _tickets:
        if "comments" not in t:
            t["comments"] = []
        if "history" not in t:
            t["history"] = []
    print(f"Loaded {len(_tickets)} tickets")


# --- Models ---

StatusLiteral = Literal["open", "acknowledged", "in_progress", "waiting_on_info", "resolved", "closed"]
PriorityLiteral = Literal["low", "medium", "high", "critical"]


class Comment(BaseModel):
    author: str
    text: str
    timestamp: str


class HistoryEntry(BaseModel):
    action: str
    actor: str
    from_status: str | None = None
    to_status: str | None = None
    timestamp: str
    notes: str | None = None


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    status: StatusLiteral
    priority: PriorityLiteral
    category: Literal["bug", "feature", "billing", "access", "performance"]
    assigned_to: Optional[str]
    created_at: str
    updated_at: str
    created_by: str
    tags: list[str]
    comments: list[Comment] = []
    history: list[HistoryEntry] = []


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


class CommentRequest(BaseModel):
    author: str
    text: str


class AcknowledgeRequest(BaseModel):
    developer: str


class RequestInfoRequest(BaseModel):
    note: str


class BulkAssignRequest(BaseModel):
    ticket_ids: list[str]
    developer: str


class TransferRequest(BaseModel):
    developer: str
    reason: str


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
    age_gt: Optional[int] = Query(None, description="Return only tickets older than N hours"),
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
    if age_gt is not None:
        cutoff = datetime.now(timezone.utc).timestamp() - (age_gt * 3600)
        result = [t for t in result if datetime.fromisoformat(t["created_at"]).timestamp() < cutoff]
    return BulkResponse(total=len(result), tickets=result)


@app.get("/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str, _auth: dict = Depends(verify_token)):
    return _find_ticket(ticket_id)


@app.post("/tickets/{ticket_id}/assign")
def assign_ticket(ticket_id: str, req: AssignRequest, auth: dict = Depends(verify_token)):
    require_write(auth)
    t = _find_ticket(ticket_id)
    prev = t["assigned_to"]
    t["assigned_to"] = req.assigned_to
    _touch(t)
    _append_history(t, action="assigned", actor=req.assigned_to,
                    notes=f"Assigned from {prev}" if prev else None)
    return {
        "id": t["id"],
        "assigned_to": t["assigned_to"],
        "updated_at": t["updated_at"],
        "message": f"Ticket {ticket_id} assigned to {req.assigned_to}",
    }


@app.post("/tickets/{ticket_id}/status")
def update_status(
    ticket_id: str,
    status: StatusLiteral = Query(...),
    auth: dict = Depends(verify_token),
):
    require_write(auth)
    t = _find_ticket(ticket_id)
    current = t["status"]

    # Reject direct transition to 'open' from states that require reopen
    if status == "open" and current in ("resolved", "closed", "waiting_on_info"):
        _error_400("invalid_transition",
                   f"Cannot transition from '{current}' to 'open' directly. Use the reopen endpoint.")

    if status not in STATUS_TRANSITIONS.get(current, set()):
        _error_400("invalid_transition",
                   f"Cannot transition from '{current}' to '{status}'.")

    from_status = current
    t["status"] = status
    _touch(t)
    _append_history(t, action="status_change", actor="system",
                    from_status=from_status, to_status=status)
    return {
        "id": t["id"],
        "status": t["status"],
        "updated_at": t["updated_at"],
    }


# --- New endpoints ---

@app.post("/tickets/{ticket_id}/escalate")
def escalate_ticket(ticket_id: str, auth: dict = Depends(verify_token)):
    require_write(auth)
    t = _find_ticket(ticket_id)

    if t["status"] not in ("open", "acknowledged"):
        _error_400("invalid_status_for_action",
                   f"Cannot escalate a ticket with status '{t['status']}'. Must be 'open' or 'acknowledged'.")
    if t["priority"] == "critical":
        _error_400("already_critical", "Ticket is already at critical priority.")

    idx = PRIORITY_LEVELS.index(t["priority"])
    from_priority = t["priority"]
    t["priority"] = PRIORITY_LEVELS[idx + 1]
    _touch(t)
    _append_history(t, action="escalated", actor="system",
                    notes=f"Priority raised from {from_priority} to {t['priority']}")
    return t


@app.post("/tickets/{ticket_id}/acknowledge")
def acknowledge_ticket(ticket_id: str, req: AcknowledgeRequest, auth: dict = Depends(verify_token)):
    require_write(auth)
    t = _find_ticket(ticket_id)

    if not t["assigned_to"]:
        _error_400("ticket_not_assigned", "Ticket must be assigned before it can be acknowledged.")
    if req.developer != t["assigned_to"]:
        _error_400("precondition_failed",
                   f"Developer '{req.developer}' does not match assigned developer '{t['assigned_to']}'.")

    # Valid from open; also allow from in_progress (re-acknowledge after reopen)
    if t["status"] not in ("open", "in_progress"):
        _error_400("invalid_transition",
                   f"Cannot acknowledge from status '{t['status']}'.")

    from_status = t["status"]
    t["status"] = "acknowledged"
    _touch(t)
    _append_history(t, action="acknowledged", actor=req.developer,
                    from_status=from_status, to_status="acknowledged")
    return t


@app.post("/tickets/{ticket_id}/comment")
def add_comment(ticket_id: str, req: CommentRequest, auth: dict = Depends(verify_token)):
    require_write(auth)
    t = _find_ticket(ticket_id)
    comment = {
        "author": req.author,
        "text": req.text,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    t["comments"].append(comment)
    _touch(t)
    _append_history(t, action="commented", actor=req.author, notes=req.text[:200])
    return t


@app.post("/tickets/{ticket_id}/reopen")
def reopen_ticket(ticket_id: str, auth: dict = Depends(verify_token)):
    require_write(auth)
    t = _find_ticket(ticket_id)

    if t["status"] not in ("resolved", "closed", "waiting_on_info"):
        _error_400("invalid_transition",
                   f"Cannot reopen from status '{t['status']}'. Must be 'resolved', 'closed', or 'waiting_on_info'.")

    from_status = t["status"]
    t["status"] = "open"
    t["assigned_to"] = None
    _touch(t)
    _append_history(t, action="reopened", actor="system",
                    from_status=from_status, to_status="open")
    return t


@app.post("/tickets/{ticket_id}/request-info")
def request_info(ticket_id: str, req: RequestInfoRequest, auth: dict = Depends(verify_token)):
    require_write(auth)
    t = _find_ticket(ticket_id)

    if t["status"] not in ("open", "acknowledged", "in_progress"):
        _error_400("invalid_transition",
                   f"Cannot request info from status '{t['status']}'. Must be 'open', 'acknowledged', or 'in_progress'.")

    from_status = t["status"]
    t["status"] = "waiting_on_info"
    _touch(t)
    # Append note as a comment
    t["comments"].append({
        "author": "system",
        "text": req.note,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    _append_history(t, action="request_info", actor="system",
                    from_status=from_status, to_status="waiting_on_info",
                    notes=req.note[:200])
    return t


@app.post("/tickets/bulk-assign")
def bulk_assign(req: BulkAssignRequest, auth: dict = Depends(verify_token)):
    require_write(auth)
    ticket_map = {t["id"]: t for t in _tickets}
    assigned = []
    skipped = []
    for tid in req.ticket_ids:
        if tid in ticket_map:
            t = ticket_map[tid]
            t["assigned_to"] = req.developer
            _touch(t)
            _append_history(t, action="assigned", actor=req.developer)
            assigned.append(tid)
        else:
            skipped.append(tid)
    return {"assigned": assigned, "skipped": skipped, "developer": req.developer}


@app.post("/tickets/{ticket_id}/transfer")
def transfer_ticket(ticket_id: str, req: TransferRequest, auth: dict = Depends(verify_token)):
    require_write(auth)
    if not req.reason or not req.reason.strip():
        raise HTTPException(status_code=422, detail="Reason is required for transfer.")
    t = _find_ticket(ticket_id)

    if not t["assigned_to"]:
        _error_400("ticket_not_assigned", "Ticket must be assigned before it can be transferred.")

    prev = t["assigned_to"]
    t["assigned_to"] = req.developer
    _touch(t)
    _append_history(t, action="transferred", actor=req.developer,
                    notes=f"Transferred from {prev}. Reason: {req.reason}")
    return t


@app.get("/tickets/{ticket_id}/history")
def get_ticket_history(ticket_id: str, _auth: dict = Depends(verify_token)):
    t = _find_ticket(ticket_id)
    return {"ticket_id": ticket_id, "history": t.get("history", [])}


@app.get("/developers")
def get_developers(_auth: dict = Depends(verify_token)):
    devs = []
    for name, info in DEVELOPERS_DATA.items():
        open_count = sum(
            1 for t in _tickets
            if t["assigned_to"] == name and t["status"] in ("open", "acknowledged", "in_progress", "waiting_on_info")
        )
        devs.append({
            "name": name,
            "open_ticket_count": open_count,
            "specialisations": info["specialisations"],
        })
    return {"developers": devs}


@app.get("/summary", response_model=SummaryResponse)
def get_summary(_auth: dict = Depends(verify_token)):
    from collections import Counter

    by_status = Counter(t["status"] for t in _tickets)
    by_priority = Counter(t["priority"] for t in _tickets)
    by_category = Counter(t["category"] for t in _tickets)
    unassigned = sum(1 for t in _tickets if t["assigned_to"] is None)

    dev_open: dict[str, int] = {}
    for t in _tickets:
        if t["assigned_to"] and t["status"] in ("open", "acknowledged"):
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
