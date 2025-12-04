# Project Restructure Summary

**Date**: December 4, 2025  
**Change**: Reorganized project to have clear `backend/` and `frontend/` folders

---

## What Changed

### Directory Structure

**Before:**
```
Evalhub/
├── api/          # Backend code
├── client/       # Frontend code
└── ...
```

**After:**
```
Evalhub/
├── backend/      # Backend code (renamed from api/)
├── frontend/     # Frontend code (renamed from client/)
└── ...
```

---

## Files Updated

### 1. Directory Renames
- `api/` → `backend/`
- `client/` → `frontend/`

### 2. Python Import Paths
All Python files updated from `api.*` to `backend.*`:

**Backend Files:**
- `backend/**/*.py` - All internal imports
- `tests/test_main.py` - Test imports
- `alembic/env.py` - Migration configuration

**Example:**
```python
# Before
from api.core.config import settings
from api.main import app

# After
from backend.core.config import settings
from backend.main import app
```

### 3. Configuration Files

**vite.config.ts:**
```typescript
// Updated paths
resolve: {
  alias: {
    "@": path.resolve(__dirname, "frontend", "src"),
  }
},
root: path.resolve(__dirname, "frontend"),
```

**tsconfig.json:**
```json
{
  "paths": {
    "@/*": ["./frontend/src/*"]
  },
  "include": ["frontend/src/**/*"]
}
```

**pyproject.toml:**
```toml
[tool.pytest.ini_options]
addopts = "-v --cov=backend --cov-report=term-missing"
```

### 4. Scripts

**start-dev.sh:**
```bash
# Updated command
uvicorn backend.main:app --reload --port 8000
```

### 5. Documentation

**Updated files:**
- `README.md` - All references to `api.main` → `backend.main`
- `SETUP.md` - All uvicorn commands updated
- Project structure diagrams updated

---

## Usage

### Starting the Backend

**Before:**
```bash
uvicorn api.main:app --reload --port 8000
```

**After:**
```bash
uvicorn backend.main:app --reload --port 8000
```

### Project Structure Reference

```
Evalhub/
├── backend/                    # 🔧 FastAPI Backend
│   ├── auth/                   # Authentication
│   ├── core/                   # Core utilities
│   │   ├── config.py          # Settings
│   │   ├── database.py        # DB connection
│   │   ├── security.py        # JWT auth
│   │   └── ...
│   ├── datasets/              # Dataset management
│   ├── evaluations/           # Evaluation tracking
│   ├── guidelines/            # Guidelines management
│   ├── users/                 # User management
│   ├── utils/                 # Utilities
│   └── main.py                # FastAPI app entry
│
├── frontend/                   # ⚛️ React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── ui/           # UI components
│   │   │   ├── layout.tsx    # Main layout
│   │   │   └── ...
│   │   ├── pages/            # Application pages
│   │   │   ├── home.tsx
│   │   │   ├── submit.tsx
│   │   │   └── ...
│   │   ├── lib/              # Utils & config
│   │   └── hooks/            # React hooks
│   ├── index.html
│   └── public/
│
├── alembic/                   # DB migrations
├── tests/                     # Backend tests
├── samples_from_evals/        # Sample data
├── attached_assets/           # Frontend assets
│
├── package.json               # Node.js deps
├── pyproject.toml             # Python deps
├── vite.config.ts             # Vite config
├── tsconfig.json              # TypeScript config
├── alembic.ini                # Alembic config
├── start-dev.sh               # Dev startup script
└── README.md                  # Documentation
```

---

## Benefits of New Structure

### ✅ Clear Separation of Concerns
- **`backend/`** - Python/FastAPI code
- **`frontend/`** - TypeScript/React code
- No ambiguity about where code lives

### ✅ Standard Convention
- Follows common full-stack project patterns
- Familiar structure for developers
- Easy to understand at a glance

### ✅ Better Organization
- Clear boundaries between frontend and backend
- Easier to set up separate deployments if needed
- Simpler to configure build tools and linters

### ✅ Scalability
- Easy to add more services (e.g., `worker/`, `shared/`)
- Can split into microservices later if needed
- Clear module boundaries

---

## Verification Checklist

- ✅ All Python imports updated from `api.*` to `backend.*`
- ✅ FastAPI app imports correctly: `from backend.main import app`
- ✅ Alembic migrations reference `backend/` directory
- ✅ Tests import from `backend.*`
- ✅ Vite config points to `frontend/` directory
- ✅ TypeScript config includes `frontend/src/**/*`
- ✅ Start script uses `backend.main:app`
- ✅ Documentation updated with new paths
- ✅ Project structure diagrams updated

---

## Development Commands

### Backend
```bash
# Start server
uvicorn backend.main:app --reload --port 8000

# Run tests
pytest

# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

### Frontend
```bash
# Start dev server
npm run dev:client

# Build for production
npm run build:client

# Type check
npm run check
```

### Full Stack
```bash
# Start both servers
./start-dev.sh
```

---

## Migration Guide for Developers

If you have local changes or branches:

### 1. Update Your Branch
```bash
git pull origin main
```

### 2. Update Local Imports
If you have uncommitted changes with `api.*` imports:
```bash
# Find and replace in your files
find . -name "*.py" -type f -exec sed -i '' 's/from api\./from backend./g' {} \;
```

### 3. Update Custom Scripts
Update any personal scripts that reference:
- `api.main:app` → `backend.main:app`
- `client/` paths → `frontend/` paths

### 4. Re-run Tests
```bash
pytest
```

---

## No Breaking Changes

✅ **API endpoints unchanged** - Still accessible at `/api/*`  
✅ **Frontend routes unchanged** - Same URLs and navigation  
✅ **Database unchanged** - No migration needed  
✅ **Environment variables unchanged** - Same `.env` configuration  
✅ **Functionality unchanged** - Only organizational structure changed  

This is purely a code organization improvement with zero impact on functionality.

---

## Questions?

- **Backend not starting?** Make sure you're using `uvicorn backend.main:app`
- **Import errors?** Verify all imports changed from `api.*` to `backend.*`
- **Frontend build failing?** Check that `vite.config.ts` points to `frontend/`
- **Tests failing?** Update test imports to use `backend.*`

Refer to:
- `README.md` - General documentation
- `SETUP.md` - Setup instructions

