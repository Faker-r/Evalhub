# Evalhub Setup Guide

Quick start guide for setting up the Evalhub development environment.

## Prerequisites

Make sure you have the following installed:
- Python 3.12 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- npm or yarn

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
cd Evalhub
```

### 2. Backend Setup

#### Install Python Dependencies

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

#### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and update with your actual values:
- `DATABASE_URL`: Your PostgreSQL connection string
- `JWT_SECRET`: Generate a secure random string
- AWS credentials (if using S3 features)

#### Setup Database

Create the database:
```bash
createdb evalhub
```

Run migrations:
```bash
alembic upgrade head
```

### 3. Frontend Setup

#### Install Node Dependencies

```bash
cd frontend && npm install
```

This will install all React, TypeScript, and UI dependencies.

### 4. Start Development Servers

You need to run both servers for full-stack development.

#### Terminal 1 - Backend (Port 8000)

```bash
uvicorn backend.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

#### Terminal 2 - Frontend (Port 5173)

```bash
cd frontend && npm run dev:client
```

You should see:
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 5. Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api/health

The frontend dev server automatically proxies API requests to the backend.

## Verification

### Test Backend

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{"status": "ok"}
```

### Test Frontend

Open http://localhost:5173 in your browser. You should see the Evalhub landing page.

## Production Build

### Build Frontend

```bash
cd frontend && npm run build:client
```

This creates optimized files in `dist/public/`

### Run Production Server

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The FastAPI server will serve both API and frontend at http://localhost:8000

## Troubleshooting

### Port Already in Use

If port 8000 or 5173 is already in use:

Backend:
```bash
uvicorn backend.main:app --reload --port 8001
```

Frontend (update vite.config.ts or use):
```bash
vite dev --port 5174
```

### Database Connection Error

- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL in `.env`
- Ensure database exists: `psql -l | grep evalhub`

### Module Not Found Errors

Backend:
```bash
pip install -e .
```

Frontend:
```bash
rm -rf node_modules package-lock.json
cd frontend && npm install
```

### CORS Errors

The backend is configured to allow requests from `http://localhost:5173`. If you change the frontend port, update `api/main.py`:

```python
allow_origins=["http://localhost:YOUR_PORT"],
```

## Next Steps

1. **Create a user account** via `/api/auth/register`
2. **Upload datasets** through the API or UI
3. **Define guidelines** for evaluation criteria
4. **Run evaluations** using the submission wizard

## Development Workflow

1. Make changes to backend code → auto-reloads via `--reload`
2. Make changes to frontend code → hot module replacement via Vite
3. Database schema changes → create migration: `alembic revision --autogenerate -m "description"`
4. Run tests: `pytest` (backend)

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)

