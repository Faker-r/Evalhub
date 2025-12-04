from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.auth.routes import router as auth_router
from backend.core.config import settings
from backend.core.logging import get_logger, setup_logging
from backend.datasets.routes import router as datasets_router
from backend.evaluations.routes import router as evaluations_router
from backend.guidelines.routes import router as guidelines_router
from backend.users.routes import router as users_router
from backend.utils.migrations import run_migrations

# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
# Temporarily disabled for initial setup
# run_migrations()

# Set up logger for this module
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Configure CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers (all under /api prefix)
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(datasets_router, prefix="/api")
app.include_router(guidelines_router, prefix="/api")
app.include_router(evaluations_router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


# Serve static frontend files in production
static_dir = Path(__file__).parent.parent / "dist" / "public"
if static_dir.exists():
    logger.info(f"Serving static files from {static_dir}")
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")
else:
    logger.warning(f"Static directory not found: {static_dir}. Run 'npm run build:client' to build the frontend.")
    
    @app.get("/")
    async def root():
        """Root endpoint - only used when frontend is not built."""
        logger.debug("Root endpoint called")
        return {
            "message": "Welcome to Evalhub API!",
            "docs": "/docs",
            "note": "Frontend not built. Run 'npm run build:client' to build the React frontend."
        }
