from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, func
from sqlalchemy import Column, Integer, DateTime, TIMESTAMP

from sqlalchemy.orm import relationship
import datetime

from .database import Base


class Key(Base):
    __tablename__ = "t_key"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(36), index=True, unique=True)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    expired_time = Column(TIMESTAMP, default=datetime.datetime.now)


class Device(Base):
    __tablename__ = "t_device"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), index=True, unique=True)
    key = Column(String(36), index=True, unique=True)
    role = Column(String(20), index=True, unique=True)
    group = Column(String(20), index=True, unique=True)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    time_created = Column(DateTime(timezone=True), server_default=func.now())
