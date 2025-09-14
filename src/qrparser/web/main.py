from fastapi import FastAPI
from . import routes


def create_app() -> FastAPI:
    app = FastAPI(
        title="QR Parser Service",
        description="Microservice for parsing QR codes from PDF files",
        version="0.1.0",
    )

    # Include routes
    app.include_router(routes.router)

    return app


app = create_app()  # ASGI app for uvicorn entrypoint
