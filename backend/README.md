# EduDeck AI

A robust, AI-powered presentation generation platform built with FastAPI, LangGraph, PostgreSQL, and ChromaDB.

## Prerequisites
- Docker and Docker Compose
- Python 3.10+

## Local Setup

1. **Clone the repository**
2. **Environment Setup**
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env with your specific API keys
   ```
3. **Start Infrastructure Services**
   ```bash
   docker-compose up -d
   ```
4. **Install Dependencies**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   pip install -r requirements.txt
   ```
5. **Run the Application**
   ```bash
   uvicorn app.main:app --reload
   ```
6. **Check Health**
   Visit `http://localhost:8000/api/v1/health`
