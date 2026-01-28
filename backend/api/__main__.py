"""Entry point for running the FastAPI development server."""

import uvicorn


def main():
    """Run the FastAPI development server with auto-reload."""
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
