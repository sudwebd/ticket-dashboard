# SupportDesk — Features & Workflows

This document describes the features of the SupportDesk ticket management system and provides step-by-step workflow guides for common tasks. It is written for support engineers and team leads who use the dashboard UI.

---

## Table of Contents

1. [Product Overview](#product-overview)
2. [Core Concepts](#core-concepts)
   - [Ticket Lifecycle](#ticket-lifecycle)
   - [Status Reference](#status-reference)
   - [Priority Reference](#priority-reference)
   - [Categories](#categories)
   - [Tags](#tags)
3. [Dashboard Screen](#dashboard-screen)
4. [Ticket Detail Screen](#ticket-detail-screen)
5. [Workflows](#workflows)
   - [Triaging a New Ticket](#1-triaging-a-new-ticket)
   - [Working a Ticket to Resolution](#2-working-a-ticket-to-resolution)
   - [Escalating a Ticket](#3-escalating-a-ticket)
   - [Requesting More Information](#4-requesting-more-information)
   - [Reopening a Closed or Resolved Ticket](#5-reopening-a-closed-or-resolved-ticket)
   - [Transferring a Ticket to Another Developer](#6-transferring-a-ticket-to-another-developer)
   - [Leaving a Comment](#7-leaving-a-comment)
   - [Viewing the Audit History](#8-viewing-the-audit-history)
6. [Status Transition Rules](#status-transition-rules)
7. [API Access Reference](#api-access-reference)

---

## Product Overview

SupportDesk is an internal ticket management system for support and engineering teams. It provides a central view of all customer support tickets, tools for routing and prioritising work, and a full audit trail of every action taken on each ticket.

**Frontend:** `http://localhost:5173`
**Backend API:** `http://localhost:8000`
**API reference:** `http://localhost:8000/docs`

---

## Core Concepts

### Ticket Lifecycle

Every ticket moves through a defined state machine. Transitions that are not permitted by the rules below are rejected at the server — the UI will display the rejection reason inline.

```
                   ┌─────────────┐
         ┌────────▶│    open     │◀────────────────────┐
         │         └──────┬──────┘                     │
         │                │                            │ reopen only
         │    ┌───────────┼───────────┐                │
         │    ▼           ▼           ▼                │
         │  ack-     in_progress  waiting_on_info ─────┘
         │  nowledged     │
         │    │           │
         │    └─────┬─────┘
         │          ▼
         │       resolved ──────────────────────────────┐
         │          │                                   │ reopen only
         │          ▼                                   │
         │        closed ◀──────────────────────────────┘
         │          │
         └──────────┘ (reopen only)
```

### Status Reference

| Status | Badge colour | Meaning |
|---|---|---|
| `open` | Green | Ticket received, not yet acknowledged or in progress |
| `acknowledged` | Cyan | Assigned developer has confirmed they have picked it up |
| `in_progress` | Blue | Actively being worked on |
| `waiting_on_info` | Yellow | Blocked — waiting for information from the customer or another team |
| `resolved` | Grey | Work complete, pending formal closure |
| `closed` | Light grey | Final state — no further action required |

### Priority Reference

| Priority | Badge colour | Meaning |
|---|---|---|
| `low` | Grey | Can be addressed in regular rotation |
| `medium` | Yellow | Standard handling, no special urgency |
| `high` | Orange | Should be picked up within the current day |
| `critical` | Red | Immediate attention required; escalate if not resolved quickly |

Priority can be raised by one level at a time using the **Escalate Priority** button. It cannot be reduced from the UI.

### Categories

| Category | Typical content |
|---|---|
| `bug` | Defects, errors, regressions |
| `feature` | New functionality requests |
| `billing` | Payment, invoice, subscription issues |
| `access` | Permissions, authentication, security |
| `performance` | Speed, latency, resource usage |

### Tags

Tickets carry two sets of tags:

- **Content tags** (applied automatically based on category): `billing`, `auth`, `performance`, `ui`, `data`
- **Workflow tags** (applied during triage or by agents): `urgent`, `regression`, `customer-reported`, `needs-repro`, `blocked`, `quick-win`

Tags are used by the Calyb connector for targeted filtering (`GET /tickets?tag=urgent`). They are read-only in the current UI.

---

## Dashboard Screen

**URL:** `/` (the default view on launch)

The Dashboard provides a high-level overview of the entire ticket queue and is the starting point for all daily triage work.

### Stat Cards (top row)

| Card | What it shows |
|---|---|
| Total open | Number of tickets currently in `open` status |
| Critical | Total tickets at `critical` priority across all statuses |
| Unassigned | Tickets with no developer assigned |
| Avg age (days) | Average age of the tickets currently visible in the table |

These numbers update when you apply filters — the average age reflects the filtered set, not the whole queue.

### Charts (middle row)

**Category breakdown (left):** Horizontal bar chart showing ticket counts per category. Useful for spotting whether a particular area (e.g. billing) is generating unusual volume.

**Developer workload (right):** Horizontal bar chart showing each developer's count of open and acknowledged tickets. Use this to spot overloaded assignees before routing new work.

### Filter Bar

Four dropdowns let you narrow the ticket table:

| Filter | Options |
|---|---|
| Status | All statuses, or any single status |
| Priority | All priorities, or any single priority |
| Category | All categories, or any single category |
| Assignee | All, Unassigned, or a specific developer |

Filters combine with AND logic. **Clear filters** resets all dropdowns and returns to the full list.

Changing any filter resets the table to page 1 automatically.

### Ticket Table

Displays up to 20 tickets per page. Columns: ID, Title, Status, Priority, Category, Assigned to.

- Click any row to navigate to the Ticket Detail screen for that ticket.
- Use **Previous / Next** to page through results.
- The row count shown ("Showing N tickets") reflects the total matching the current filters.

---

## Ticket Detail Screen

**URL:** `/tickets/:id`

This is the primary workspace for acting on a single ticket. It has two panels.

### Left Panel

| Section | Content |
|---|---|
| Header | Ticket title, priority badge, status badge, category badge |
| Description | Full problem description |
| Metadata grid | Created time, category, tags, last updated, current assignee |
| Comments | Thread of comments; input box to post a new comment |
| History | Collapsible full audit log of every action taken on the ticket |

### Right Panel — Actions Card

All mutations happen here. The available buttons change depending on the ticket's current state.

| Control | When visible | What it does |
|---|---|---|
| Update status (dropdown) | Always | Changes ticket status via the state machine; rejects invalid transitions |
| Assign to (dropdown + button) | Always | Assigns or reassigns the ticket to a developer |
| Acknowledge (button) | Ticket is assigned AND status is `open` or `in_progress` | Records that the assigned developer has taken ownership |
| Escalate Priority (button) | Status is `open` or `acknowledged` AND priority is not `critical` | Raises priority one level |
| Reopen (button) | Status is `resolved` or `closed` | Clears the assignee and returns ticket to `open` |
| Mark as resolved (link) | Status is not `resolved` or `closed` | Shortcut to set status to `resolved` and return to dashboard |

If an action is rejected by the server (e.g. an invalid status transition), the error reason is displayed inline in the Actions card in red.

---

## Workflows

### 1. Triaging a New Ticket

**Goal:** Take an unassigned `open` ticket, route it to the right developer, and confirm it has been picked up.

**Steps:**

1. From the **Dashboard**, set the **Status** filter to `open` and the **Assignee** filter to `Unassigned`.
2. Review the **Developer workload** chart on the right to identify who has capacity.
3. Click the ticket you want to triage.
4. On the Ticket Detail screen, open the **Assign to** dropdown in the Actions card and select the developer.
5. Click **Assign**. The metadata grid updates to show the new assignee.
6. The developer should then open the ticket and click **Acknowledge** to confirm they have picked it up. The status moves from `open` → `acknowledged`.

> The Acknowledge button is only visible to the assigned developer's session. It requires the ticket to be assigned and the status to be `open` or `in_progress`.

---

### 2. Working a Ticket to Resolution

**Goal:** Progress a ticket through `acknowledged` → `in_progress` → `resolved` → `closed`.

**Steps:**

1. Open the ticket from the Dashboard or directly via its URL.
2. When you begin work, use the **Update status** dropdown to change from `acknowledged` to `in_progress`. Click the dropdown and select **In Progress** — the status saves immediately.
3. Add comments as you investigate using the Comments section (see [Leaving a Comment](#7-leaving-a-comment)).
4. When the fix is complete, either:
   - Select `resolved` from the **Update status** dropdown, or
   - Click **Mark as resolved** at the bottom of the Actions card (this also returns you to the Dashboard).
5. Once the customer has confirmed or the resolution is verified, open the ticket again and change status to `closed` via the dropdown.

> `resolved` → `closed` is the only forward transition from `resolved`. To move backward, use **Reopen**.

---

### 3. Escalating a Ticket

**Goal:** Raise the urgency of a ticket that is more severe than its current priority suggests.

**Steps:**

1. Open the ticket from the Dashboard.
2. Confirm the status is `open` or `acknowledged` — escalation is not permitted on tickets already in progress or resolved.
3. Click **Escalate Priority** in the Actions card.
4. The priority badge updates immediately (e.g. `medium` → `high`). The change is recorded in the History panel.
5. Repeat if needed — each click raises priority by one step up to `critical`.

> The Escalate Priority button disappears once the ticket reaches `critical` priority.

**Shortcut for batch escalation:** Use the API endpoint `POST /tickets/{id}/escalate` (with `agent-key-003`) to escalate programmatically without opening each ticket in the UI.

---

### 4. Requesting More Information

**Goal:** Pause work on a ticket and block it until the customer or another team provides missing details.

**Steps:**

1. Open the ticket. Status must be `open`, `acknowledged`, or `in_progress`.
2. Via the API (`POST /tickets/{id}/request-info` with `agent-key-003` or `dashboard-key-001`), submit a note explaining what information is needed. *(This action is not yet surfaced as a button in the UI — use the API directly or via the agent.)*
3. The status changes to `waiting_on_info` (Yellow badge). The note is automatically appended as a system comment.
4. The Update status dropdown in the UI will now only allow transitions via **Reopen** (since `waiting_on_info` can only return to `open`).
5. When the required information arrives, click **Reopen** (or call `POST /tickets/{id}/reopen`). The ticket returns to `open` with no assignee — re-assign and continue.

---

### 5. Reopening a Closed or Resolved Ticket

**Goal:** Return a ticket that was prematurely closed or needs further work back to active status.

**Steps:**

1. Find the ticket. Use the **Status** filter set to `resolved` or `closed` on the Dashboard.
2. Open the ticket.
3. Click **Reopen** in the Actions card (visible only when status is `resolved` or `closed`).
4. The ticket status returns to `open`. The current assignee is automatically cleared so the ticket can be re-triaged fresh.
5. Re-assign via the **Assign to** control and continue the triage workflow.

> The History panel will record the reopen event, including what status it was reopened from.

---

### 6. Transferring a Ticket to Another Developer

**Goal:** Move an already-assigned ticket to a different developer, with a recorded reason.

**Steps:**

1. Open the ticket. It must already have an assignee — you cannot transfer an unassigned ticket.
2. Use `POST /tickets/{id}/transfer` via the API with a body of `{ "developer": "...", "reason": "..." }`. *(Transfer is not yet a UI button — use the API or the agent directly.)*
3. The assignee updates. The previous assignee and the reason are recorded in the History panel as a `transferred` entry.

> If you just want to reassign without a formal transfer record, use the **Assign to** dropdown in the Actions card — this overwrites the assignee without requiring a reason.

---

### 7. Leaving a Comment

**Goal:** Record investigation notes, customer updates, or team communication on a ticket.

**Steps:**

1. Open any ticket (comments are allowed at any status).
2. Scroll to the **Comments** section on the left panel.
3. Use the author dropdown to select your name.
4. Type your comment in the text field.
5. Click **Post** or press **Enter**. The comment appears immediately above the input.

> Comments are permanent and visible to anyone with access to the ticket. Each comment is also captured as a `commented` entry in the History log.

---

### 8. Viewing the Audit History

**Goal:** Review every action that has ever been taken on a ticket — status changes, assignments, escalations, comments, reopens.

**Steps:**

1. Open the ticket.
2. Scroll to the bottom of the left panel.
3. Click the **History (N)** toggle to expand the audit log.
4. Each entry shows: timestamp, action type, actor, from/to status (for transitions), and any notes.
5. Click the toggle again to collapse.

**Programmatic access:** `GET /tickets/{id}/history` returns the full ordered log in JSON — accessible to all three API keys.

---

## Status Transition Rules

The server enforces a strict state machine. Any transition not listed below will return `HTTP 400` with a `precondition_failed` error body.

| From | Allowed transitions |
|---|---|
| `open` | `acknowledged`, `in_progress`, `waiting_on_info` |
| `acknowledged` | `in_progress`, `waiting_on_info` |
| `in_progress` | `resolved`, `waiting_on_info` |
| `waiting_on_info` | `open` via **Reopen** only |
| `resolved` | `closed`, or `open` via **Reopen** only |
| `closed` | `open` via **Reopen** only |

> Direct `POST /tickets/{id}/status?status=open` from `resolved`, `closed`, or `waiting_on_info` is rejected. Always use the **Reopen** endpoint or button.

**Error response format:**

```json
{
  "error": "precondition_failed",
  "reason": "invalid_transition",
  "detail": "Cannot transition from 'closed' to 'in_progress'."
}
```

**Reason codes:**

| Code | Trigger |
|---|---|
| `invalid_transition` | Status change violates the state machine |
| `ticket_not_assigned` | Action requires the ticket to be assigned first |
| `already_critical` | Escalate called on a ticket already at `critical` priority |
| `invalid_status_for_action` | Action not permitted from the current status |
| `already_assigned` | Assignment conflict |

---

## API Access Reference

| Key | Role | UI access | Permitted endpoints |
|---|---|---|---|
| `dashboard-key-001` | Admin | Used by the frontend | All endpoints except `/calyb/planner-test` |
| `calyb-key-002` | Reader | Calyb connector only | `GET /tickets`, `GET /tickets/{id}`, `GET /tickets/{id}/history`, `GET /developers`, `GET /summary`, `GET /health` |
| `agent-key-003` | Agent | Data agents / test harness | All mutation endpoints + `POST /calyb/planner-test` |

All keys use Bearer token authentication: `Authorization: Bearer <key>`

**Bulk operations available via API only (not yet in UI):**

| Endpoint | Purpose |
|---|---|
| `POST /tickets/bulk-assign` | Assign a list of ticket IDs to one developer in a single call |
| `POST /tickets/{id}/transfer` | Transfer with a required reason recorded in history |
| `POST /tickets/{id}/request-info` | Move to `waiting_on_info` with a blocking note |
| `GET /tickets?age_gt=N` | Fetch tickets older than N hours |
| `GET /developers` | List all developers with open ticket counts and specialisations |
