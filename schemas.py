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

    class Config:
        orm_mode: True
