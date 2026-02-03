from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from api.auth.routes import router as auth_router
from api.benchmarks.routes import router as benchmarks_router
from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.datasets.routes import router as datasets_router
from api.evaluation_comparison.routes import router as evaluation_comparison_router
from api.evaluations.routes import router as evaluations_router
from api.evaluations.service import shutdown_process_pool
from api.guidelines.routes import router as guidelines_router
from api.leaderboard.routes import router as leaderboard_router
from api.models_and_providers.routes import router as models_and_providers_router
from api.users.routes import router as users_router
from api.utils.migrations import run_migrations

# Set up logging configuration
setup_logging()


# Set up logger for this module
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events."""
    # Startup
    logger.info("Starting Evalhub application")
    yield
    # Shutdown
    logger.info("Shutting down Evalhub application")
    shutdown_process_pool()
    logger.info("Process pool shutdown complete")


app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Include routers under /api prefix
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(datasets_router)
api_router.include_router(guidelines_router)
api_router.include_router(evaluations_router)
api_router.include_router(evaluation_comparison_router)
api_router.include_router(leaderboard_router)
api_router.include_router(benchmarks_router)
api_router.include_router(models_and_providers_router)

# Include the API router in the main app
app.include_router(api_router)


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": "Welcome to Evalhub!"}
