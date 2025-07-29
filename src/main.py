from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .database import Base, engine, SessionLocal
from .models import User
from .schemas import CreateUser, ResponseUser

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
    new_user = User(name=user.name, email=str(user.email), password=user.password)
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