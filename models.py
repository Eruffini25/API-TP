from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

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