from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from pydantic import BaseModel
from passlib.context import CryptContext

DATABASE_URL = "postgresql://user:password@db/dbname"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Models
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50), unique=True, nullable=False),
    Column("password", String, nullable=False),
    Column("role", String(50), nullable=False, default="user")
)

logs = Table(
    "logs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime, default=func.now(), nullable=False),
    Column("domain", String(100)),
    Column("ip_address", String(45)),
    Column("service_name", String(100)),
    Column("message", String, nullable=False),
    Column("severity", String(20), nullable=False)
)

metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class LogCreate(BaseModel):
    domain: str
    ip_address: str
    service_name: str
    message: str
    severity: str

# Routes
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    db.execute(users.insert().values(username=user.username, password=hashed_password, role="user"))
    db.commit()
    return {"username": user.username, "role": "user"}

@app.post("/logs/")
def create_log(log: LogCreate, db: Session = Depends(get_db)):
    db.execute(logs.insert().values(
        domain=log.domain,
        ip_address=log.ip_address,
        service_name=log.service_name,
        message=log.message,
        severity=log.severity
    ))
    db.commit()
    return {"message": "Log created successfully"}

@app.get("/logs/{severity}")
def read_logs(severity: str, db: Session = Depends(get_db)):
    result = db.execute(logs.select().where(logs.c.severity == severity)).fetchall()
    return result

@app.get("/logs/{id}")
def read_log(id: int, db: Session = Depends(get_db)):
    result = db.execute(logs.select().where(logs.c.id == id)).fetchone()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
