from pydantic import BaseModel


class SettingResponse(BaseModel):
    key: str
    type: str
    value: str
    tag: str | None = None
    description: str | None = None
    editable: bool = True


class SettingCreate(BaseModel):
    key: str
    type: str
    value: str
    tag: str | None = None
    description: str | None = None
    editable: bool = True


class SettingUpdate(BaseModel):
    type: str | None = None
    value: str | None = None
    tag: str | None = None
    description: str | None = None
