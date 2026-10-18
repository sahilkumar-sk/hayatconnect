# 🩸 HayatConnect

**Blood Donation Matching Platform for Karachi**

HayatConnect connects patients who urgently need blood with nearby, verified donors using AI-powered matching. Built to solve the real problem of families scrambling on social media to find blood donors at odd hours.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, React, Tailwind CSS, TypeScript |
| Backend | FastAPI (Python), async |
| Database | PostgreSQL 16 + Alembic migrations |
| Cache | Redis |
| Auth | JWT + phone OTP (Twilio) |
| AI/ML | scikit-learn, XGBoost (donor ranking & fraud detection) |
| Maps | Leaflet + OpenStreetMap |
| Notifications | Firebase Cloud Messaging + SMS |

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- PostgreSQL 16
- Redis

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Edit with your credentials

# Create database
createdb hayatconnect

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
hayatconnect/
├── frontend/              # Next.js 14 app
│   └── src/
│       ├── app/           # Pages (App Router)
│       ├── components/    # Reusable UI components
│       └── lib/           # API client, utilities
├── backend/               # FastAPI app
│   ├── app/
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic request/response schemas
│   │   ├── routers/       # API route handlers
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   └── tests/
└── README.md
```

## License

MIT
