from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas import LoginRequest, ResponseToken
from src.security.auth import create_access_token, verify_password
from src.models import User
from src.dependencies import get_db
import logging

router = APIRouter(prefix="/login", tags=["auth"])
logger = logging.getLogger(__name__)

@router.post("", response_model=ResponseToken)
def create_token(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info("Login attempt for email: %s", request.email)
    user = db.query(User).filter(User.email == str(request.email)).first()
    if not user:
        logger.error("User not found: %s", request.email)
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(request.password, user.password):
        logger.error("Incorrect password for email: %s", request.email)
        raise HTTPException(status_code=401, detail="Incorrect password")
    token = create_access_token({"id": user.id, "sub": user.email})
    logger.info("Token created successfully for user: %s", request.email)
    return {
        "access_token": token,
        "token_type": "bearer",
        "status_code": 200,
        "message": "¡Bienvenido de nuevo, parcero! Ya podés comenzar a chatear.",
    }
