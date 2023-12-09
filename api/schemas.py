from typing import Any
from pydantic import BaseModel


class Info(BaseModel):
    deviceId: str
    key: str

    class Config:
        from_attributes = True


class Rsp(BaseModel):
    status: str = "ok"
    code: str = "0000"
    msg: str = ""
    data: Any = None

    class Config:
        from_attributes = True
