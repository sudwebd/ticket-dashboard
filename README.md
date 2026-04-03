# Support Ticket Dashboard

Full-stack support ticket dashboard with a React frontend and FastAPI backend.

## Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python generate_tickets.py     # generates tickets.json
uvicorn main:app --reload      # runs on http://localhost:8000
```

### Frontend (separate terminal)

```bash
cd frontend
npm install
npm run dev                    # runs on http://localhost:5173
```

Backend must be running before the frontend will show any data.

## API

- `GET /health` — health check
- `GET /tickets/page` — paginated tickets (used by frontend)
- `GET /tickets` — bulk tickets (Calyb connector only)
- `GET /tickets/{id}` — single ticket
- `POST /tickets/{id}/assign` — assign ticket
- `POST /tickets/{id}/status?status=...` — update status
- `GET /summary` — dashboard summary stats

OpenAPI spec: http://localhost:8000/openapi.json
