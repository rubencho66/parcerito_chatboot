"""Database connection and session management for the application.
This module sets up the SQLAlchemy engine, session local, and base class for models."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from src.env import CONNECTION

engine = create_engine(CONNECTION)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
