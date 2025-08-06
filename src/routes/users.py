from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from src.schemas import CreateUser, ResponseUser
from src.models import User
from src.security.auth import hash_password
from src.dependencies import get_db
import logging

router = APIRouter(prefix="/users", tags=["users"])
logger = logging.getLogger(__name__)

@router.post("", response_model=ResponseUser)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    logger.info("Creating user with email: %s", user.email)
    hash_pass = hash_password(user.password)
    new_user = User(name=user.name, email=str(user.email), password=hash_pass)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        logger.info("User created successfully: %s", new_user.email)
        return new_user
    except IntegrityError as exc:
        db.rollback()
        logger.warning("Email already registered: %s", user.email)
        raise HTTPException(status_code=400, detail="Email already registered") from exc

@router.get("", response_model=list[ResponseUser])
def get_users(db: Session = Depends(get_db)):
    logger.info("Fetching all users")
    users = db.query(User).all()
    return users
