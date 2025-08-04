"""main.py"""

from fastapi import FastAPI
from src.routes import users, auth, chat
from src.exception_handlers import register_exception_handlers
from src.logging_config import configure_logging
from src.database import Base, engine

def create_app() -> FastAPI:
    """App factory for FastAPI application."""
    configure_logging()
    app = FastAPI()

    # Register routers
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(chat.router)

    # Register exception handlers
    register_exception_handlers(app)

    # Database initialization (optional: move to startup event)
    Base.metadata.create_all(bind=engine)

    return app

app = create_app()
