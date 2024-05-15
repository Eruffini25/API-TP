from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Log
from schemas import LogCreate, Log as LogSchema

router = APIRouter()

@router.post("/logs/", response_model=LogSchema)
async def create_log(log: LogCreate, db: Session = Depends(get_db)):
    db_log = Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/logs/{log_id}", response_model=LogSchema)
async def read_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(Log).filter(Log.id == log_id).first()
    if log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

@router.get("/logs/info", response_model=list[LogSchema])
async def read_logs_info(db: Session = Depends(get_db)):
    logs = db.query(Log).filter(Log.severity == 'info').all()
    return logs
