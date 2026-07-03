# Running EduDeck AI

Follow these steps to set up and run the EduDeck AI backend from a fresh clone.

## 1. Prerequisites
- Python 3.10+ (Verified on 3.14.2)
- Docker & Docker Compose
- Git

## 2. Clone Repository
```bash
git clone https://github.com/DevanshGanatra/EduDeck-AI.git
cd EduDeck-AI
```

## 3. Create Virtual Environment
**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```
**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

## 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

## 5. Environment Variables
Copy `.env.example` to `.env` and fill in your OpenAI API Key.
```bash
cp .env.example .env
```

## 6. Start Infrastructure (Docker)
Start PostgreSQL and ChromaDB in the background:
```bash
docker compose up -d
```
*(Postgres runs on port 5432, ChromaDB runs on port 8000)*

## 7. Run Migrations (Alembic)
Ensure tables are created:
```bash
alembic upgrade head
```
*(If no alembic setup exists for MVP, tables will auto-create via SQLAlchemy on startup if configured)*

## 8. Start FastAPI Backend
Because ChromaDB occupies port 8000, we run FastAPI on port 8080:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

## 9. Verify and Test
- **Swagger UI**: Visit `http://localhost:8080/docs`
- **Health Check**: `GET http://localhost:8080/api/v1/health`

## 10. Sample Workflow
1. Use `/api/v1/auth/register` to create a user.
2. Use `/api/v1/auth/login` to get a JWT token.
3. Click "Authorize" in Swagger to attach the token.
4. Create a project at `POST /api/v1/projects`.
5. Upload a PDF at `POST /api/v1/documents/upload`.
6. Vectorize at `POST /api/v1/retrieval/project/{id}/vectorize`.
7. Generate PPT at `POST /api/v1/generation/generate`.
