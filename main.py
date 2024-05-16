from fastapi import FastAPI, Depends, HTTPException, APIRouter, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import Column, Integer, String, DateTime, create_engine, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List, Optional
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
    is_admin = Column(Boolean, default=False)

# Schémas Pydantic
class LogBase(BaseModel):
    domain: str
    ip_address: str
    service_name: str
    message: str
    severity: str

class LogCreate(LogBase):
    pass

class LogSchema(LogBase):
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

class UserSchema(UserBase):
    is_admin: bool

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Fonctions d'authentification et utilitaires
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

# Création de l'application FastAPI
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup():
    db = SessionLocal()
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        hashed_password = get_password_hash("adminpassword")
        new_user = User(username="admin", hashed_password=hashed_password, is_admin=True)
        db.add(new_user)
        db.commit()
    db.close()

@app.on_event("shutdown")
def shutdown():
    pass

# Définition des routes
router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password, is_admin=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Routes Syslog
@router.post("/logs/", response_model=LogSchema)
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    db_log = Log(
        domain=log.domain,
        ip_address=log.ip_address,
        service_name=log.service_name,
        message=log.message,
        severity=log.severity
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/logs/info", response_model=List[LogSchema])
def read_all_logs(db: Session = Depends(get_db)):
    logs = db.query(Log).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

@router.get("/logs/{severity}", response_model=List[LogSchema])
def read_logs_by_severity(severity: str, db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.severity == severity).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

# Routes d'administration Syslog
@router.put("/logs/{id}", response_model=LogSchema)
def update_log(id: int, log: LogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_log = db.query(Log).filter(Log.id == id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    db_log.domain = log.domain
    db_log.ip_address = log.ip_address
    db_log.service_name = log.service_name
    db_log.message = log.message
    db_log.severity = log.severity
    db.commit()
    db.refresh(db_log)
    return db_log

@router.delete("/logs/{id}")
def delete_log(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin_user)):
    db_log = db.query(Log).filter(Log.id == id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    db.delete(db_log)
    db.commit()
    return {"detail": "Log deleted"}

app.include_router(router)
