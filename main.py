from fastapi import FastAPI, Depends, HTTPException, status
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel
from passlib.context import CryptContext

DATABASE_URL = "postgresql://user:password@db/dbname"

database = Database(DATABASE_URL)
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

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

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
async def create_user(user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    query = users.insert().values(username=user.username, password=hashed_password, role="user")
    await database.execute(query)
    return {"username": user.username, "role": "user"}

@app.post("/logs/")
async def create_log(log: LogCreate):
    query = logs.insert().values(
        domain=log.domain,
        ip_address=log.ip_address,
        service_name=log.service_name,
        message=log.message,
        severity=log.severity
    )
    await database.execute(query)
    return {"message": "Log created successfully"}

@app.get("/logs/{severity}")
async def read_logs(severity: str):
    query = logs.select().where(logs.c.severity == severity)
    return await database.fetch_all(query)

@app.get("/logs/{id}")
async def read_log(id: int):
    query = logs.select().where(logs.c.id == id)
    return await database.fetch_one(query)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
