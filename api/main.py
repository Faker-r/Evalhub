from fastapi import FastAPI

from api.auth.routes import router as auth_router
from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.datasets.routes import router as datasets_router
from api.evaluations.routes import router as evaluations_router
from api.guidelines.routes import router as guidelines_router
from api.leaderboard.routes import router as leaderboard_router
from api.users.routes import router as users_router
from api.utils.migrations import run_migrations

# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
run_migrations()

# Set up logger for this module
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Include routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(datasets_router)
app.include_router(guidelines_router)
app.include_router(evaluations_router)
app.include_router(leaderboard_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": "Welcome to Evalhub!"}
