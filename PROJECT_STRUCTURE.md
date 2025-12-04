# Evalhub Project Structure

Complete overview of the project organization after restructuring.

---

## Directory Layout

```
Evalhub/                              # Project root
│
├── backend/                          # 🐍 Python/FastAPI Backend
│   ├── auth/                         # Authentication module
│   │   ├── __init__.py
│   │   ├── routes.py                 # Auth endpoints (login, register)
│   │   ├── schemas.py                # Pydantic models
│   │   └── service.py                # Business logic
│   │
│   ├── core/                         # Core utilities
│   │   ├── config.py                 # Settings & environment vars
│   │   ├── database.py               # DB connection & session
│   │   ├── exceptions.py             # Custom exceptions
│   │   ├── logging.py                # Logging configuration
│   │   ├── s3.py                     # AWS S3 integration
│   │   └── security.py               # JWT & password hashing
│   │
│   ├── datasets/                     # Dataset management
│   │   ├── models.py                 # SQLAlchemy models
│   │   ├── repository.py             # Database operations
│   │   ├── routes.py                 # API endpoints
│   │   ├── schemas.py                # Request/response models
│   │   └── service.py                # Business logic
│   │
│   ├── evaluations/                  # Evaluation tracking
│   │   ├── models.py                 # Trace & TraceEvent models
│   │   ├── repository.py             # Database operations
│   │   ├── routes.py                 # API endpoints
│   │   ├── schemas.py                # Request/response models
│   │   └── service.py                # Business logic
│   │
│   ├── guidelines/                   # Evaluation guidelines
│   │   ├── models.py                 # SQLAlchemy models
│   │   ├── repository.py             # Database operations
│   │   ├── routes.py                 # API endpoints
│   │   ├── schemas.py                # Request/response models
│   │   └── service.py                # Business logic
│   │
│   ├── users/                        # User management
│   │   ├── models.py                 # User model
│   │   ├── repository.py             # Database operations
│   │   ├── routes.py                 # API endpoints
│   │   ├── schemas.py                # Request/response models
│   │   └── service.py                # Business logic
│   │
│   ├── utils/                        # Utility functions
│   │   └── migrations.py             # Migration helpers
│   │
│   └── main.py                       # FastAPI app entry point
│
├── frontend/                         # ⚛️ React/TypeScript Frontend
│   ├── src/                          # Source code
│   │   ├── components/               # React components
│   │   │   ├── ui/                   # Reusable UI components (40+)
│   │   │   │   ├── button.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   └── ...
│   │   │   ├── cards.tsx             # Dataset & guideline cards
│   │   │   ├── layout.tsx            # Main layout with navbar
│   │   │   ├── leaderboard-table.tsx # Model rankings table
│   │   │   └── login-modal.tsx       # Authentication modal
│   │   │
│   │   ├── pages/                    # Application pages
│   │   │   ├── home.tsx              # Landing page
│   │   │   ├── submit.tsx            # Evaluation submission wizard
│   │   │   ├── datasets.tsx          # Dataset browser
│   │   │   ├── guidelines.tsx        # Guidelines catalog
│   │   │   ├── compare.tsx           # Model comparison
│   │   │   ├── results.tsx           # Evaluation results
│   │   │   └── not-found.tsx         # 404 page
│   │   │
│   │   ├── lib/                      # Utilities & configuration
│   │   │   ├── queryClient.ts        # TanStack Query setup
│   │   │   └── utils.ts              # Helper functions
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── use-mobile.tsx        # Mobile detection
│   │   │   └── use-toast.ts          # Toast notifications
│   │   │
│   │   ├── App.tsx                   # Main app component
│   │   ├── main.tsx                  # React entry point
│   │   └── index.css                 # Global styles
│   │
│   ├── public/                       # Static assets
│   │   └── favicon.png
│   │
│   ├── index.html                    # HTML entry point
│   ├── package.json                  # Node.js dependencies & scripts
│   ├── tsconfig.json                 # TypeScript configuration
│   ├── vite.config.ts                # Vite bundler configuration
│   ├── postcss.config.js             # PostCSS configuration
│   └── components.json               # Shadcn/ui configuration
│
├── alembic/                          # 🗄️ Database Migrations
│   ├── versions/                     # Migration files
│   │   ├── 001_add_datasets_and_guidelines.py
│   │   ├── 002_add_traces_tables.py
│   │   ├── 3dee83604016_initial_migration.py
│   │   └── ef2910566747_add_users_table.py
│   ├── env.py                        # Alembic environment
│   └── script.py.mako                # Migration template
│
├── tests/                            # 🧪 Backend Tests
│   ├── __init__.py
│   └── test_main.py                  # API tests
│
├── samples_from_evals/               # 📊 Sample Data
│   ├── sample_datasets/              # Example datasets (JSONL)
│   │   ├── joke_fruits.jsonl
│   │   ├── mtbench_simplified.jsonl
│   │   └── ...
│   ├── sample_guidelines/            # Example guidelines (YAML)
│   │   └── humor.yaml
│   └── sample_traces/                # Example evaluation runs
│       ├── joke_fruits_run.jsonl
│       └── ...
│
├── attached_assets/                  # 🎨 Frontend Assets
│   └── generated_images/
│       └── abstract_geometric_composition_with_mint_accents.png
│
├── .github/                          # GitHub configuration
├── .vscode/                          # VS Code settings
│
├── .env.example                      # Environment variables template
├── .gitignore                        # Git ignore rules
├── .pre-commit-config.yaml           # Pre-commit hooks
├── .python-version                   # Python version
│
├── alembic.ini                       # Alembic configuration
├── pyproject.toml                    # Python dependencies & tools
├── uv.lock                           # UV lock file
│
├── start-dev.sh                      # 🚀 Development startup script
├── test_script.py                    # Test utilities
│
├── README.md                         # 📖 Main documentation
├── SETUP.md                          # Setup instructions
├── RESTRUCTURE_SUMMARY.md            # Restructure details
├── PROJECT_STRUCTURE.md              # This file
│
└── LICENSE                           # MIT License
```

---

## Key Characteristics

### ✅ Clean Separation
- **Backend** - All Python/FastAPI code in `backend/`
- **Frontend** - All TypeScript/React code in `frontend/`
- **No mixing** - Each has its own dependencies and configs

### ✅ Self-Contained Modules
- **Backend modules** - Each has models, routes, schemas, service, repository
- **Frontend** - All configs live in the `frontend/` directory
- **Easy navigation** - Clear where to find specific functionality

### ✅ Standard Conventions
- Follows common full-stack patterns
- Backend uses repository pattern
- Frontend uses component-based architecture

---

## Working Directories

### Backend Development
```bash
# Work from project root
cd Evalhub/

# Start backend
uvicorn backend.main:app --reload --port 8000

# Run tests
pytest

# Create migration
alembic revision --autogenerate -m "description"
```

### Frontend Development
```bash
# Work from frontend directory
cd Evalhub/frontend/

# Install dependencies
npm install

# Start dev server
npm run dev:client

# Build for production
npm run build:client

# Type check
npm run check
```

### Full-Stack Development
```bash
# From project root
./start-dev.sh
```

---

## Configuration Files

### Root Level (Project-wide)
- `.env` - Environment variables (create from `.env.example`)
- `pyproject.toml` - Python dependencies and tool configs
- `alembic.ini` - Database migration settings
- `start-dev.sh` - Convenience script for development

### Backend-Specific
- All Python code uses imports like `from backend.core.config import settings`
- No separate config files needed (uses `pyproject.toml`)

### Frontend-Specific
All in `frontend/` directory:
- `package.json` - Dependencies & npm scripts
- `tsconfig.json` - TypeScript compiler options
- `vite.config.ts` - Build tool configuration
- `postcss.config.js` - CSS processing
- `components.json` - UI component library config

---

## Import Patterns

### Backend (Python)
```python
# Absolute imports from backend package
from backend.core.config import settings
from backend.core.database import get_db
from backend.auth.service import AuthService
from backend.datasets.models import Dataset
```

### Frontend (TypeScript)
```typescript
// Path aliases configured in tsconfig.json
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import generatedImage from "@assets/generated_images/image.png";
```

---

## Build Outputs

### Frontend Build
```
dist/
└── public/              # Built frontend (created by vite build)
    ├── index.html
    ├── assets/
    │   ├── index-[hash].js
    │   └── index-[hash].css
    └── ...
```

### Backend Serves Frontend
In production, FastAPI serves the built frontend from `dist/public/`

---

## Dependencies

### Backend (Python)
Managed in `pyproject.toml`:
- FastAPI - Web framework
- SQLAlchemy - ORM
- Alembic - Migrations
- Pydantic - Validation
- Boto3 - AWS S3
- PyJWT - Authentication

### Frontend (Node.js)
Managed in `frontend/package.json`:
- React 19 - UI framework
- TypeScript - Type safety
- Vite - Build tool
- Tailwind CSS - Styling
- Radix UI - Component primitives
- TanStack Query - Data fetching
- Wouter - Routing

---

## Environment Variables

Located in `.env` at project root:
```env
# Backend uses these
DATABASE_URL=postgresql://...
JWT_SECRET=...
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
DEBUG=true
```

Frontend uses relative URLs in development (proxied by Vite) and production (same origin).

---

## Development Workflow

### 1. Initial Setup
```bash
# Install backend dependencies
uv sync  # or pip install -e .

# Install frontend dependencies
cd frontend && npm install
```

### 2. Daily Development
```bash
# Option 1: Use convenience script
./start-dev.sh

# Option 2: Manual (two terminals)
# Terminal 1:
uvicorn backend.main:app --reload --port 8000

# Terminal 2:
cd frontend && npm run dev:client
```

### 3. Access
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/*
- API Docs: http://localhost:8000/docs

---

## Production Deployment

### Build
```bash
# Build frontend
cd frontend && npm run build:client
```

### Deploy
```bash
# Single server serves both
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Backend automatically serves:
- API at `/api/*`
- Frontend at `/*` (from `dist/public/`)

---

## Benefits of This Structure

✅ **Clear organization** - No confusion about where code lives  
✅ **Independent development** - Frontend and backend can evolve separately  
✅ **Easy onboarding** - New developers understand structure immediately  
✅ **Scalable** - Can add more services (e.g., `worker/`, `shared/`)  
✅ **Standard patterns** - Follows industry best practices  
✅ **Clean dependencies** - Each part has its own dependency management  

---

## Quick Reference

| Task | Command | Directory |
|------|---------|-----------|
| Start backend | `uvicorn backend.main:app --reload` | Root |
| Start frontend | `npm run dev:client` | `frontend/` |
| Install backend deps | `uv sync` or `pip install -e .` | Root |
| Install frontend deps | `npm install` | `frontend/` |
| Run backend tests | `pytest` | Root |
| Build frontend | `npm run build:client` | `frontend/` |
| Create migration | `alembic revision --autogenerate -m "msg"` | Root |
| Apply migrations | `alembic upgrade head` | Root |
| Type check frontend | `npm run check` | `frontend/` |

---

This structure provides a solid foundation for a professional full-stack application! 🎉

