from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
import database
import auth

router = APIRouter()

@router.get("/logs/{severity}", response_model=List[schemas.Log])
def read_logs_by_severity(severity: str, db: Session = Depends(database.get_db)):
    logs = db.query(models.Log).filter(models.Log.severity == severity).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs

@router.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
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

@router.get("/logs/info", response_model=List[schemas.Log])
def read_all_logs(db: Session = Depends(database.get_db)):
    logs = db.query(models.Log).all()
    if not logs:
        raise HTTPException(status_code=404, detail="Logs not found")
    return logs
