from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .models import logs
from .database import database

router = APIRouter()

@router.post("/logs/")
async def create_log(log: LogCreate, db: Session = Depends(get_db)):
    query = logs.insert().values(
        domain=log.domain,
        ip_address=log.ip_address,
        service_name=log.service_name,
        message=log.message,
        severity=log.severity
    )
    await database.execute(query)
    return {"message": "Log created successfully"}

@router.get("/logs/{severity}")
async def read_logs(severity: str, db: Session = Depends(get_db)):
    query = logs.select().where(logs.c.severity == severity)
    return await database.fetch_all(query)

@router.get("/logs/{id}")
async def read_log(id: int, db: Session = Depends(get_db)):
    query = logs.select().where(logs.c.id == id)
    return await database.fetch_one(query)

@router.delete("/logs/{id}")
async def delete_log(id: int, db: Session = Depends(get_db)):
    query = logs.delete().where(logs.c.id == id)
    await database.execute(query)
    return {"message": "Log deleted successfully"}

@router.put("/logs/{id}")
async def update_log(id: int, log: LogCreate, db: Session = Depends(get_db)):
    query = logs.update().where(logs.c.id == id).values(
        domain=log.domain,
        ip_address=log.ip_address,
        service_name=log.service_name,
        message=log.message,
        severity=log.severity
    )
    await database.execute(query)
    return {"message": "Log updated successfully"}

app.include_router(router)
