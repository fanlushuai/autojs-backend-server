import string
from tokenize import String
from sqlalchemy.orm import Session

from . import models, schemas
from datetime import datetime


def create_key(db: Session, key: str, expired_time: int):
    db_key = models.Key(key=key, expired_time=datetime.fromtimestamp(expired_time))
    db.add(db_key)
    db.commit()
    db.refresh(db_key)
    return db_key


def get_key(db: Session, key: str):
    return (
        db.query(models.Key)
        .filter(models.Key.key == key)
        .filter(models.Key.expired_time > datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        .first()
    )


def create_device(db: Session, key: str, device_id: str):
    db_device = models.Device(device_id=device_id, key=key)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_device(db: Session, device_id: str):
    return db.query(models.Device).filter(models.Device.device_id == device_id).first()


def list_device(db: Session):
    return db.query(models.Device).all()


# def get_users(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.User).offset(skip).limit(limit).all()
