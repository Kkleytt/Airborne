from database.models.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, Float, Text, Boolean, TIMESTAMP, BigInteger, JSON, Date


class KnowledgeBase(Base):
    __tablename__ = "knowledge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created: Mapped[int] = mapped_column(TIMESTAMP, nullable=False)
    edited: Mapped[int] = mapped_column(TIMESTAMP, nullable=False)
    editor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSON, nullable=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class NewsBase(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created: Mapped[int] = mapped_column(TIMESTAMP, nullable=False)
    creator: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(Text, nullable=True)
    text_id: Mapped[int] = mapped_column(Integer, nullable=False)
    images_id: Mapped[dict] = mapped_column(JSON, nullable=True)
    files_id: Mapped[dict] = mapped_column(JSON, nullable=True)
    keyboard_id: Mapped[int] = mapped_column(Integer, nullable=False)
    views: Mapped[dict] = mapped_column(JSON, nullable=True)
    invite: Mapped[dict] = mapped_column(JSON, nullable=True)
    ignores: Mapped[dict] = mapped_column(JSON, nullable=True)


class UsersBase(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    nick: Mapped[str] = mapped_column(Text, nullable=True)
    birthday: Mapped[str] = mapped_column(Date, nullable=True)
    phone: Mapped[str] = mapped_column(Text, nullable=True)
    name_first: Mapped[str] = mapped_column(Text, nullable=True)
    name_second: Mapped[str] = mapped_column(Text, nullable=True)
    name_manual: Mapped[str] = mapped_column(Text, nullable=True)
    request_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    request_first: Mapped[int] = mapped_column(Integer, nullable=True)
    request_last: Mapped[int] = mapped_column(Integer, nullable=True)
    blocked_status: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    blocked_time: Mapped[str] = mapped_column(TIMESTAMP, nullable=False, default='2200-01-01 00:00:00')
    ip: Mapped[str] = mapped_column(Text, nullable=True)
    device: Mapped[str] = mapped_column(Text, nullable=True)
    role: Mapped[str] = mapped_column(Text, nullable=False, default="user")
    rating: Mapped[float] = mapped_column(Float, nullable=False, default=0)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    groups: Mapped[dict] = mapped_column(JSON, nullable=True)


class GroupsBase(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    admins: Mapped[dict] = mapped_column(JSON, nullable=False, default='[]')
    users: Mapped[dict] = mapped_column(JSON, nullable=False, default='[]')
    invite: Mapped[dict] = mapped_column(JSON, nullable=False, default='[]')
    events: Mapped[dict] = mapped_column(JSON, nullable=False, default='[]')


class EventsBase(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[int] = mapped_column(TIMESTAMP, nullable=False)
    location: Mapped[str] = mapped_column(Text, nullable=True)
    users: Mapped[dict] = mapped_column(JSON, nullable=False, default='[]')
    invite: Mapped[dict] = mapped_column(JSON, nullable=False, default='[]')
