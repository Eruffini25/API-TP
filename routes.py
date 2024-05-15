# routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas, database

router = APIRouter()

@router.get("/logs/{severity}", response_model=List[schemas.Log])
def read_logs_by_severity(severity: str, db: Session = Depends(database.get_db)):
    logs = db.query(models.Log).filter(models.Log.severity == severity).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

@router.post("/users/")
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = models.User(username=user.username, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/logs/")
def create_log(log: schemas.LogCreate, db: Session = Depends(database.get_db)):
    db_log = models.Log(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log
