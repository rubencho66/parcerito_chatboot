from src.database import SessionLocal
import logging

def get_db():
    logger = logging.getLogger(__name__)
    logger.debug("Creating a new database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
