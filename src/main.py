from . import env
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import User
from .schemas import ErrorResponse, SecurityContext, CreateUser, ResponseToken, ResponseUser, LoginRequest, ChatRequest, ChatResponse
from .security.auth import hash_password, verify_password, create_access_token, get_security_context
from .chat_model import instanciate_chat_model, ask_to_model

app = FastAPI()
model = instanciate_chat_model()

#database
Base.metadata.create_all(bind=engine)

#dependency to get session from database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.detail, statusCode=exc.status_code).model_dump()
    )

@app.post("/users", response_model=ResponseUser)
def create_user(user: CreateUser, db: Session = Depends(get_db)):
    hash_pass = hash_password(user.password)
    new_user = User(name=user.name, email=str(user.email), password=hash_pass)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")


@app.get("/users", response_model=list[ResponseUser])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


@app.post("/login", response_model=ResponseToken)
def create_token(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == str(request.email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_access_token({"id": user.id, "sub": user.email})
    return {"access_token": token,
            "token_type": "bearer",
            "status_code": 200,
            "message": "¡Bienvenido de nuevo, parcero! Ya podés comenzar a chatear."}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, security_context: SecurityContext = Depends(get_security_context), db: Session = Depends(get_db)):
    chat_response = ask_to_model(model, request.message, request.conversation_id)
    if not chat_response:
        raise HTTPException(status_code=500, detail="Model is not working.")
    return ChatResponse(reply=chat_response, statusCode=200, conversation_id=request.conversation_id)
