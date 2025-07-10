from pydantic import BaseModel
from datetime import datetime


class Knowledge:
    class Response(BaseModel):
        id: int
        created: datetime
        edited: datetime
        editor: int
        type: str
        tag: str
        description: str
        meta: dict
        value: str

    class Create(BaseModel):
        editor: int
        type: str | None = "text"
        tag: str | None = None
        description: str | None = None
        meta: dict | None = {}
        value: str

    class Update(BaseModel):
        edited: datetime
        editor: int
        type: str | None = "text"
        tag: str | None = None
        description: str | None = None
        meta: dict | None = {}
        value: str

