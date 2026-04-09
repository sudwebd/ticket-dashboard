"""Generate tickets.json with reproducible random data."""

import json
import random
from datetime import datetime, timedelta, timezone

RANDOM_SEED = 42
TICKET_COUNT = 200

DEVELOPERS = ["Alice Chen", "Bob Patel", "Carlos Rivera", "Diana Osei", "Ethan Kim"]
DEVELOPER_WEIGHTS = [28, 25, 22, 15, 10]

STATUSES = ["open", "acknowledged", "in_progress", "waiting_on_info", "resolved", "closed"]
STATUS_WEIGHTS = [30, 10, 20, 5, 20, 15]

PRIORITIES = ["low", "medium", "high", "critical"]
PRIORITY_WEIGHTS = [25, 40, 25, 10]

CATEGORIES = ["bug", "feature", "billing", "access", "performance"]
CATEGORY_WEIGHTS = [20, 20, 20, 20, 20]

TAGS = ["urgent", "regression", "customer-reported", "needs-repro", "blocked", "quick-win"]

# Semantic tags for ticket content seeding
CONTENT_TAGS = {
    "bug": ["billing", "auth", "performance", "ui", "data"],
    "feature": ["ui", "auth", "data", "performance", "billing"],
    "billing": ["billing", "data", "ui"],
    "access": ["auth", "ui", "data"],
    "performance": ["performance", "data", "ui"],
}

UNASSIGNED_CHANCE_OPEN = 0.35
UNASSIGNED_CHANCE_OTHER = 0.10

TITLES: dict[str, list[str]] = {
    "bug": [
        "HTTP 500 on checkout when cart has 50+ items",
        "Login fails silently on Safari 17.2",
        "CSV export truncates rows after 10,000 records",
        "Session expires mid-form causing data loss",
        "Timezone offset breaks scheduled reports",
        "File upload returns 413 but file is under limit",
        "Search results pagination skips page 3",
        "Password reset email contains broken link",
        "Dark mode toggle does not persist across tabs",
        "Webhook delivery retries exceed configured max",
        "Date picker shows wrong month on first open",
        "API rate limiter counts OPTIONS as requests",
        "CORS error when embedding dashboard in iframe",
        "Drag-and-drop reorder saves in wrong sequence",
    ],
    "feature": [
        "Add Slack integration for ticket notifications",
        "Support bulk ticket reassignment from list view",
        "Add custom field support for ticket metadata",
        "Export tickets to PDF with company branding",
        "Implement saved search filters per user",
        "Add two-factor authentication option",
        "Support Markdown in ticket descriptions",
        "Create public-facing status page",
        "Add SLA timer display on ticket cards",
        "Implement ticket merge for duplicates",
        "Add keyboard shortcuts for common actions",
        "Support multiple email addresses per contact",
        "Add audit log for ticket field changes",
        "Create mobile-responsive ticket view",
    ],
    "billing": [
        "Customer charged twice for annual plan renewal",
        "Discount code SAVE20 not applying at checkout",
        "Plan upgrade not activating premium features",
        "VAT calculation wrong for EU customers",
        "Invoice PDF shows previous company address",
        "Refund issued but balance not updated in dashboard",
        "Trial extension not reflected in billing portal",
        "Payment method update fails with 3D Secure cards",
        "Prorated charge incorrect when switching mid-cycle",
        "Coupon stacking bypass allows negative totals",
        "Annual billing toggle shows wrong monthly price",
        "Tax exempt status not carrying over to new invoices",
        "Stripe webhook missing for subscription cancellation",
        "Credit note not generated after partial refund",
    ],
    "access": [
        "Viewer role can access admin settings via direct URL",
        "SSO login loop when IdP session expires",
        "Deactivated user retains API key access for 24h",
        "IP allowlist not enforced on mobile app endpoints",
        "Guest link shares expose internal ticket comments",
        "Role change not reflected until manual cache clear",
        "OAuth scope escalation via token refresh flow",
        "Team member removal does not revoke shared links",
        "SAML assertion replay accepted within 5-minute window",
        "Password policy not enforced on API-created accounts",
        "Two-factor bypass when switching auth providers",
        "Audit log missing entries for permission changes",
        "Service account tokens never expire despite policy",
        "Cross-tenant data leak via malformed GraphQL query",
    ],
    "performance": [
        "Dashboard takes 12 seconds to load with 1000+ tickets",
        "Search index 4 hours stale after bulk import",
        "API p99 latency spiked to 3.2s after v2.4.1 deploy",
        "Report generation OOMs on datasets over 500MB",
        "WebSocket reconnect storm during rolling deploys",
        "Database connection pool exhausted at 200 concurrent users",
        "Image thumbnail generation blocks main thread",
        "Cache miss rate jumped from 5% to 40% after migration",
        "Elasticsearch queries timing out for wildcard searches",
        "CSV export takes 45 seconds for 10k rows",
        "Background job queue backed up 2 hours during peak",
        "GraphQL N+1 queries on ticket list with comments",
        "Redis memory usage growing 500MB/day from orphaned keys",
        "Page load time degrades linearly with filter count",
    ],
}

DESCRIPTIONS: dict[str, list[str]] = {
    "bug": [
        "When a user adds more than 50 items to their cart and proceeds to checkout, the server returns an HTTP 500 error. The checkout page shows a generic error message. This was first reported by a customer on March 12th and affects both web and mobile clients.",
        "On Safari 17.2, clicking the login button does nothing — no error, no redirect, no console output. The issue does not reproduce on Chrome or Firefox. Multiple customers have reported being unable to access their accounts from macOS Sonoma.",
        "Exporting tickets to CSV works for small datasets but silently truncates at exactly 10,000 rows. The file appears complete with headers and no error indication. Customers with large accounts are receiving incomplete exports.",
        "Users filling out the multi-step support request form lose all entered data when their session expires mid-process. The form does not warn about impending expiration or save draft state. This has caused significant user frustration.",
        "Scheduled reports configured for specific timezones are being sent at the wrong time. The offset appears to be inverted — UTC+5 users receive reports as if they were UTC-5. This started after the daylight saving time transition.",
        "File uploads under the 10MB limit are being rejected with a 413 Payload Too Large error. The actual threshold appears to be around 8.2MB. The upload progress bar reaches 100% before the error appears, confusing users.",
        "Navigating through search results, page 3 is completely skipped. Clicking 'Next' from page 2 goes directly to page 4. The URL parameter updates correctly but the API returns page 4 data. Affects all search queries with more than 2 pages.",
        "Password reset emails contain a link pointing to the old domain name. Clicking the link results in a DNS resolution failure. This has been blocking all password resets since the domain migration on February 28th.",
        "The dark mode toggle in user preferences works within the current tab but reverts to light mode when a new tab is opened. The preference is stored in sessionStorage instead of localStorage, causing it to not persist.",
        "Webhook delivery is configured to retry 3 times but actually retries 7 times. Each retry doubles the delay, causing some webhooks to be delivered up to 2 hours after the initial failure. This is overwhelming receiving services with duplicate events.",
    ],
    "feature": [
        "Our team uses Slack as the primary communication channel. We need ticket notifications (new, assigned, status change) pushed to a configurable Slack channel. Currently the team manually checks the dashboard every 30 minutes and misses urgent tickets.",
        "Support managers need to reassign tickets in bulk when a team member goes on leave. Currently each ticket must be opened individually and reassigned. With 40+ tickets per developer, this takes over an hour of manual work.",
        "Different customer segments require different metadata on tickets (e.g., enterprise needs contract ID, retail needs order number). Custom fields would eliminate the current workaround of stuffing metadata into the description field.",
        "The legal team requires ticket exports in PDF format with company branding for compliance audits. Currently they screenshot the UI or copy-paste into Word documents. A native PDF export would save approximately 4 hours per monthly audit.",
        "Power users create the same complex filter combinations repeatedly. Saved filters would allow them to bookmark frequent queries like 'my open critical tickets' or 'unassigned billing issues this week' and access them with one click.",
        "Several enterprise customers have requested two-factor authentication as a requirement for their security compliance. Currently we only support password-based auth which does not meet SOC 2 requirements for some of our clients.",
        "Ticket descriptions currently only support plain text. Support agents frequently need to include code snippets, formatted logs, and structured reproduction steps. Markdown support would significantly improve ticket readability.",
        "Customers have requested a public-facing status page that shows current system health and any ongoing incidents. This would reduce inbound support tickets during outages by approximately 30% based on industry benchmarks.",
    ],
    "billing": [
        "Customer (account #AC-4892) reports being charged $299 twice on March 5th for their annual Pro plan renewal. Stripe shows two successful charges: ch_3NkL9x and ch_3NkLBw, 4 seconds apart. The customer's card was charged $598 total. Immediate refund of duplicate charge needed.",
        "Discount code SAVE20 returns 'invalid code' at checkout despite being active in the promotions dashboard. The code was created on Feb 1st with no expiration date. Testing confirms it fails for all plan types. Approximately 50 customers have reported this issue.",
        "Customer upgraded from Basic ($29/mo) to Premium ($99/mo) three days ago. Payment was processed successfully (ORD-2024-8821) but premium features like advanced analytics and API access remain locked. Manual feature flag toggle is the current workaround.",
        "EU customers in Germany, France, and Netherlands are being charged 19% VAT regardless of their actual country rate. France should be 20%, Netherlands 21%. This affects approximately 340 active subscriptions and may have compliance implications.",
        "All invoices generated after March 1st show the company's previous address (123 Old Street) instead of the current address (456 New Avenue). The billing settings page shows the correct address. This appears to be a caching issue in the PDF generation service.",
        "A refund of $49.99 was processed for order ORD-2024-7156 on March 8th. The Stripe dashboard confirms the refund but the customer's account balance in our system still shows the original charge. The billing history page has no record of the refund.",
        "Customer was granted a 14-day trial extension via the admin panel but the billing portal still shows the original trial end date. The customer received an email confirming the extension. The mismatch is causing confusion and the customer may be charged early.",
        "Customers using 3D Secure enabled cards cannot update their payment method. The update flow redirects to the bank's 3DS page but the callback URL returns a 404. This affects approximately 15% of our European customer base.",
    ],
    "access": [
        "Users with the 'viewer' role can navigate directly to /admin/settings and view sensitive configuration including API keys and webhook secrets. The sidebar correctly hides the admin link but no server-side authorization check exists on the settings endpoint.",
        "When the identity provider session expires, users entering the SSO login flow get caught in an infinite redirect loop between our app and the IdP. The browser eventually shows 'too many redirects' after approximately 15 cycles. Affects all SSO-configured organizations.",
        "When a user account is deactivated via the admin panel, their existing API keys remain functional for up to 24 hours. The key revocation runs as a background job that only executes once daily at midnight UTC. This creates a security window for terminated employees.",
        "The IP allowlist configured in organization security settings is enforced on web endpoints but not on mobile API endpoints (/api/mobile/*). A user connecting from a blocked IP can still access all data through the mobile app. Discovered during a security audit.",
        "Guest share links for tickets expose the internal comments tab which may contain sensitive information about other customers or internal processes. The share link should only show the ticket description and status, not the full comment thread.",
        "When an admin changes a user's role from 'editor' to 'viewer', the change does not take effect until the user clears their browser cache or the server-side session cache expires (4 hours). During this window the user retains editor permissions.",
        "The OAuth token refresh flow does not validate the original scope grant. A token initially issued with read-only scope can be refreshed to request read-write scope without user consent. This was identified by an external security researcher.",
        "When a team member is removed from an organization, their previously created shared links remain active. These links continue to provide access to ticket data even though the user no longer has an account. There is no mechanism to bulk-revoke links by user.",
    ],
    "performance": [
        "The main dashboard page takes over 12 seconds to render when the account has more than 1,000 tickets. Profiling shows the bottleneck is a non-indexed COUNT query that runs for each status category. Adding composite indexes should reduce this to under 500ms.",
        "After running a bulk ticket import (5,000+ tickets), the search index takes 4 hours to fully update. During this window, newly imported tickets do not appear in search results. The indexer processes records sequentially rather than in batches.",
        "Following the v2.4.1 deployment on March 3rd, API p99 latency increased from 800ms to 3.2 seconds. The regression correlates with the new audit logging middleware that performs a synchronous database write on every request. Moving to async logging should resolve this.",
        "Generating the monthly analytics report for accounts with over 500MB of ticket data causes the worker process to run out of memory (OOM killed). The report builder loads the entire dataset into memory. Streaming or chunked processing is needed.",
        "During rolling deployments, all connected WebSocket clients attempt to reconnect simultaneously, creating a thundering herd that overwhelms the new pods. The reconnection uses a fixed 1-second delay instead of exponential backoff with jitter.",
        "Under load testing at 200 concurrent users, the application exhausts the database connection pool (max 20 connections) and subsequent requests queue for up to 30 seconds. The pool size needs to be increased and connection timeout reduced.",
        "Thumbnail generation for uploaded images runs synchronously on the main API thread, blocking all other requests for 2-3 seconds per image. This should be offloaded to a background worker queue to prevent request handling degradation.",
        "After migrating from Redis 6 to Redis 7, the cache miss rate jumped from 5% to 40%. Investigation shows the serialization format changed and existing cached entries are being treated as misses. A cache warm-up script is needed post-migration.",
    ],
}

SAMPLE_COMMENTS = [
    "I can reproduce this consistently on my end.",
    "This looks related to the deployment last week.",
    "Customer is asking for an update on this.",
    "I've narrowed the root cause to the caching layer.",
    "Waiting on access to the staging environment to verify.",
    "Escalating to the infrastructure team for input.",
    "Confirmed this is a regression from v2.4.1.",
    "Workaround documented in the internal wiki.",
]


def random_created_at(status: str) -> str:
    now = datetime.now(timezone.utc)
    if status in ("resolved", "closed"):
        days_back = random.uniform(0, 30)
    else:
        days_back = random.uniform(0, 14)
    created = now - timedelta(days=days_back)
    return created.isoformat()


def random_updated_at(created_at_str: str) -> str:
    created = datetime.fromisoformat(created_at_str)
    now = datetime.now(timezone.utc)
    diff = (now - created).total_seconds()
    if diff <= 0:
        return created.isoformat()
    offset = random.uniform(0, diff)
    updated = created + timedelta(seconds=offset)
    return updated.isoformat()


def generate_one(index: int) -> dict:
    category = random.choices(CATEGORIES, weights=CATEGORY_WEIGHTS)[0]
    status = random.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
    priority = random.choices(PRIORITIES, weights=PRIORITY_WEIGHTS)[0]
    unassigned_p = UNASSIGNED_CHANCE_OPEN if status == "open" else UNASSIGNED_CHANCE_OTHER
    assigned_to = (
        None
        if random.random() < unassigned_p
        else random.choices(DEVELOPERS, weights=DEVELOPER_WEIGHTS)[0]
    )
    # Tickets in acknowledged/in_progress/waiting_on_info should always be assigned
    if status in ("acknowledged", "in_progress", "waiting_on_info") and assigned_to is None:
        assigned_to = random.choices(DEVELOPERS, weights=DEVELOPER_WEIGHTS)[0]

    created_at = random_created_at(status)

    # Pick content tags based on category
    content_tag_pool = CONTENT_TAGS.get(category, ["data"])
    num_tags = random.randint(1, min(3, len(content_tag_pool)))
    content_tags = random.sample(content_tag_pool, k=num_tags)

    # Also include 0-2 workflow tags
    workflow_tags = random.sample(TAGS, k=random.randint(0, 2))

    # Combine, deduplicate
    all_tags = list(dict.fromkeys(content_tags + workflow_tags))

    # Generate some comments for non-open tickets
    comments = []
    if status != "open" and random.random() < 0.6:
        num_comments = random.randint(1, 3)
        created_dt = datetime.fromisoformat(created_at)
        for _ in range(num_comments):
            comment_offset = random.uniform(0, (datetime.now(timezone.utc) - created_dt).total_seconds())
            comments.append({
                "author": random.choice(DEVELOPERS),
                "text": random.choice(SAMPLE_COMMENTS),
                "timestamp": (created_dt + timedelta(seconds=comment_offset)).isoformat(),
            })

    # Generate history entries
    history = []
    created_dt = datetime.fromisoformat(created_at)
    history.append({
        "action": "created",
        "actor": random.choice(DEVELOPERS),
        "from_status": None,
        "to_status": "open",
        "timestamp": created_at,
        "notes": None,
    })
    if assigned_to:
        assign_offset = random.uniform(0, max(1, (datetime.now(timezone.utc) - created_dt).total_seconds() * 0.3))
        history.append({
            "action": "assigned",
            "actor": assigned_to,
            "from_status": None,
            "to_status": None,
            "timestamp": (created_dt + timedelta(seconds=assign_offset)).isoformat(),
            "notes": None,
        })
    if status not in ("open",):
        status_offset = random.uniform(0, max(1, (datetime.now(timezone.utc) - created_dt).total_seconds() * 0.6))
        history.append({
            "action": "status_change",
            "actor": assigned_to or "system",
            "from_status": "open",
            "to_status": status,
            "timestamp": (created_dt + timedelta(seconds=status_offset)).isoformat(),
            "notes": None,
        })

    return {
        "id": f"TKT-{index:04d}",
        "title": random.choice(TITLES[category]),
        "description": random.choice(DESCRIPTIONS[category]),
        "status": status,
        "priority": priority,
        "category": category,
        "assigned_to": assigned_to,
        "created_at": created_at,
        "updated_at": random_updated_at(created_at),
        "created_by": random.choice(DEVELOPERS),
        "tags": all_tags,
        "comments": comments,
        "history": history,
    }


def main():
    random.seed(RANDOM_SEED)
    tickets = [generate_one(i) for i in range(TICKET_COUNT)]

    with open("tickets.json", "w") as f:
        json.dump(tickets, f, indent=2)

    # Print distribution stats
    from collections import Counter

    print(f"Generated {len(tickets)} tickets\n")

    status_counts = Counter(t["status"] for t in tickets)
    print("By status:")
    for s, c in sorted(status_counts.items()):
        print(f"  {s}: {c}")

    priority_counts = Counter(t["priority"] for t in tickets)
    print("\nBy priority:")
    for p, c in sorted(priority_counts.items()):
        print(f"  {p}: {c}")

    category_counts = Counter(t["category"] for t in tickets)
    print("\nBy category:")
    for cat, c in sorted(category_counts.items()):
        print(f"  {cat}: {c}")

    unassigned = sum(1 for t in tickets if t["assigned_to"] is None)
    print(f"\nUnassigned: {unassigned}")

    dev_counts = Counter(
        t["assigned_to"] for t in tickets if t["assigned_to"] is not None and t["status"] == "open"
    )
    print("\nDeveloper load (open tickets):")
    for dev, c in sorted(dev_counts.items(), key=lambda x: x[1]):
        print(f"  {dev}: {c}")

    with_comments = sum(1 for t in tickets if t["comments"])
    print(f"\nTickets with comments: {with_comments}")

    tag_counts = Counter(tag for t in tickets for tag in t["tags"])
    print("\nTag distribution:")
    for tag, c in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {c}")


if __name__ == "__main__":
    main()
