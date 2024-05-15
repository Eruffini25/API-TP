from pydantic import BaseModel
from datetime import datetime

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

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode: True
