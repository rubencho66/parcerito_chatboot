from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import User
from .schemas import CreateUser, ResponseToken, ResponseUser, LoginRequest
from .security.auth import hash_password, verify_password, create_access_token

app = FastAPI()

#database
Base.metadata.create_all(bind=engine)

#dependency to get session from database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

    token = create_access_token({"sub": user.email})
    return {"access_token": token,
            "token_type": "bearer",
            "status_code": 200,
            "message": "¡Bienvenido de nuevo, parcero! Ya podés comenzar a chatear."}