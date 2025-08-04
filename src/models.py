"""models.py"""

from sqlalchemy import Column, Integer, String

from src.database import Base


class User(Base):
    """User model for the application, representing a user in the database."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
