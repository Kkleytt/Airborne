from pydantic import BaseModel  # Базовая модель данных
from datetime import datetime  # Типа данных datetime


class Knowledge:
    class Response(BaseModel):
        id: int
        created: datetime
        edited: datetime
        editor: int
        type: str
        tag: str
        description: str
        value: str

    class Create(BaseModel):
        editor: int
        type: str | None = "text"
        tag: str | None = None
        description: str | None = None
        value: str

    class Update(BaseModel):
        edited: datetime
        editor: int
        type: str | None = "text"
        tag: str | None = None
        description: str | None = None
        value: str
