# JurystAi - LegalTech SaaS for Kazakhstan

**AI-powered RAG system for Kazakhstan legislation** with comprehensive legal code search, JWT authentication, and production-ready deployment infrastructure.

## Project Overview

JurystAi is a next-generation LegalTech platform that indexes all 9 Kazakhstan legal codes and provides intelligent search.

### 9 Kazakhstan Legal Codes Indexed
1. Constitution of Kazakhstan
2. Criminal Code
3. Civil Code
4. Code of Criminal Procedure
5. Code of Civil Procedure
6. Labour Code
7. Family Code
8. Administrative Code
9. Tax Code

## Tech Stack

**Backend:**
- FastAPI 0.104+ (Python 3.11)
- SQLAlchemy ORM
- PostgreSQL/Supabase
- Alembic migrations
- PyJWT with refresh tokens
- Groq AI + Google GenAI

**Frontend:**
- Next.js 14 with TypeScript
- React 18
- TailwindCSS
- Supabase client

**Infrastructure:**
- Railway (Backend deployment)
- Vercel (Frontend deployment)
- GitHub Actions (CI/CD)
- Docker & Docker Compose (Local dev)

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 14+ (or use Supabase)
- Git

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/K09-0/juristai.git
cd juristai
```

### 2. Copy Environment Variables
```bash
cp .env.example .env
```

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

This starts:
- PostgreSQL on localhost:5432
- Backend on http://localhost:8000
- Frontend on http://localhost:3000

### 4. Manual Setup (Without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Backend Environment Variables
```env
DATABASE_URL=postgresql://user:pass@host/db
GROQ_API_KEY=<your-groq-api-key>
GOOGLE_GENAI_API_KEY=<your-google-genai-key>
SECRET_KEY=<your-jwt-secret-key>
ENV=development|production
DEBUG=true|false
PORT=8000
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### Database Migrations
```bash
alembic revision --autogenerate -m "message"
alembic upgrade head
alembic downgrade -1
```

## API Documentation

### Health Check
```bash
curl http://localhost:8000/health
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /health | Health check |
| GET | /status | Detailed status |
| GET | /docs | Swagger UI |
| POST | /auth/register | Register user |
| POST | /auth/login | Login |
| POST | /auth/refresh | Refresh token |
| GET | /legislation/codes | List codes |
| GET | /legislation/search | Search legislation |
| POST | /admin/index-legislation | Trigger indexing |

## Production Deployment

### Deploy Backend to Railway

1. Connect GitHub account to Railway
2. Create project and select repository
3. Add environment variables in Railway dashboard
4. Railway auto-deploys on push to main

### Deploy Frontend to Vercel

1. Import GitHub repo to Vercel
2. Configure build: Framework = Next.js, Root = frontend
3. Add environment variables
4. Vercel auto-deploys on push to main

### Configure DNS

For juristai.site:

**API (api.juristai.site):**
- Type: CNAME
- Value: railway-domain.railway.app

**Frontend (www.juristai.site):**
- Type: CNAME
- Value: cname.vercel-dns.com

## Security

- JWT tokens: Access 30min, Refresh 7 days
- Password: bcrypt with 12 salt rounds
- CORS: Production domains only
- Database: SSL/TLS in production
- Audit logging: All user actions tracked

## Project Structure

```
juristai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── auth/jwt_auth.py
│   ├── alembic/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── next.config.js
│   └── tailwind.config.js
├── .github/workflows/ci.yml
├── docker-compose.yml
└── README.md
```

## License

Proprietary - JurystAi Project

---

**JurystAi** - Making Kazakhstan legislation accessible. 🇰🇿 ⚖️