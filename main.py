from fastapi import FastAPI, Depends, HTTPException, APIRouter
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List
import bcrypt
from passlib.context import CryptContext

# Configuration de la base de données
DATABASE_URL = "postgresql://user:password@db:5432/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Définition des modèles
class Log(Base):
    __tablename__ = 'logs'
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    ip_address = Column(String, index=True)
    service_name = Column(String, index=True)
    message = Column(String)
    severity = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Schémas Pydantic
class LogBase(BaseModel):
    domain: str
    ip_address: str
    service_name: str
    message: str
    severity: str

class LogCreate(LogBase):
    pass

class Log(LogBase):
    id: int
    timestamp: datetime

    class Config:
        orm_mode: True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode: True

# Fonctions d'authentification et utilitaires
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Définition des routes
router = APIRouter()

@router.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/logs/")
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    db_log = Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return {"message": "Log created successfully"}

@router.get("/logs/info", response_model=List[Log])
def read_all_logs(db: Session = Depends(get_db)):
    logs = db.query(Log).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

@router.get("/logs/{severity}", response_model=List[Log])
def read_logs_by_severity(severity: str, db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.severity == severity).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

# Création de l'application FastAPI
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
async def startup():
    pass

@app.on_event("shutdown")
async def shutdown():
    pass

app.include_router(router)
