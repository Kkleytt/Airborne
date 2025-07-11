from sqlalchemy.orm import Mapped, mapped_column  # Преобразование данных
from sqlalchemy import Integer, Float, Text, Boolean, TIMESTAMP, BigInteger, JSON, Date, String  # Типы SQL данных
from sqlalchemy.sql import func  # SQL функции

from database.models.basemodel import BaseModel  # Базовая модель данных ORM


# Класс для хранения компонентов (Текста, Фото, Аудио, Файлы, Клавиатуры)
class KnowledgeModel(BaseModel):
    """
    id: ID компонента
    created: Timestamp дата создания компонента
    edited: Timestamp дата последнего изменения компонента
    editor: Telegram ID пользователя который сделал последнее изменение компонента
    type: Тип компонента (text, photo, audio, document, file, keyboard, location) (Текст длиной не более 16 символов)
    tag: Тэг для группировки компонентов (Текст длиной не более 64 символов)
    description: Описание компонента (Текст любой длины)
    value: Значение компонента (Текст любой длины)
    """

    __tablename__ = "knowledge"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created: Mapped[int] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    edited: Mapped[int] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    editor: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[str] = mapped_column(String(16), nullable=False, server_default="text")
    tag: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


# Класс для хранения новостей
class NewsModel(BaseModel):
    """
    id: ID новости
    created: Timestamp дата создания новости
    creator: Telegram ID пользователя создавшего запись
    name: Название новости (Текст любой длины)
    tag: Тэг для группировки новостей (Текст длиной не более 64 символов)
    text_id: ID текста из таблицы knowledge
    images_id: Список ID изображений из таблицы knowledge
    files_id: Список ID файлов из таблицы knowledge
    keyboard_id: ID клавиатуры из таблицы knowledge
    views: Список Telegram ID пользователей просмотревших запись
    invites: Список Telegram ID кому придет оповещение о новой записи
    ignores: Список Telegram ID кому нельзя показывать запись
    """

    __tablename__ = "news"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    created: Mapped[int] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    creator: Mapped[int] = mapped_column(BigInteger, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(String(64), nullable=True)
    text_id: Mapped[int] = mapped_column(Integer, nullable=False)
    images_id: Mapped[dict] = mapped_column(JSON, nullable=True)
    files_id: Mapped[dict] = mapped_column(JSON, nullable=True)
    keyboard_id: Mapped[int] = mapped_column(Integer, nullable=False)
    views: Mapped[dict] = mapped_column(JSON, nullable=True, server_default="[]")
    invites: Mapped[dict] = mapped_column(JSON, nullable=True, server_default="[]")
    ignores: Mapped[dict] = mapped_column(JSON, nullable=True, server_default="[]")


# Класс для хранения пользователей
class UsersModel(BaseModel):
    """
    id: Telegram ID пользователя
    nick: Telegram никнейм пользователя (Текст длиной не более 64 символов)
    birthday: День рождение пользователя (Дата)
    phone: Телефон пользователя (Текст длиной не более 16 символов)
    name_first: Telegram имя пользователя (Текст любой длины)
    name_second: Telegram фамилия пользователя (Текст любой длины)
    name_manual: Полное ФИО пользователя вручную введенное (Текст любой длины)
    request_total: Общее количество Telegram запросов от пользователя
    request_first: Timestamp время отправки первого Telegram запроса
    request_last: Timestamp время отправки последнего Telegram запроса
    blocked_status: Статус блокировки пользователя (True-заблокирован, False-разблокирован)
    blocked_time: Время окончания блокировки пользователя
    ip: Последний IP адрес пользователя (Текст длиной не более 32 символов)
    device: Последнее устройство пользователя (Текст длиной не более 64 символов)
    role: Роль пользователя (user, trusted, admin, root) (Текст длиной не более 16 символов)
    rating: Рейтинг пользователя на основе отзывов о нем
    description: Описание себя как пользователя (Текст любой длины)
    groups: Список групп в которых состоит пользователь
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, nullable=False)
    nick: Mapped[str] = mapped_column(String(64), nullable=True)
    birthday: Mapped[str] = mapped_column(Date, nullable=True)
    phone: Mapped[str] = mapped_column(String(16), nullable=True)
    name_first: Mapped[str] = mapped_column(Text, nullable=True)
    name_second: Mapped[str] = mapped_column(Text, nullable=True)
    name_manual: Mapped[str] = mapped_column(Text, nullable=True)
    request_total: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    request_first: Mapped[int] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    request_last: Mapped[int] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    blocked_status: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    blocked_time: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    ip: Mapped[str] = mapped_column(String(32), nullable=True)
    device: Mapped[str] = mapped_column(String(64), nullable=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False, server_default="user")
    rating: Mapped[float] = mapped_column(Float, nullable=False, server_default="0")
    description: Mapped[str] = mapped_column(Text, nullable=True)
    groups: Mapped[dict] = mapped_column(JSON, nullable=True, server_default="[]")


# Класс для хранения групп пользователей
class GroupsModel(BaseModel):
    """
    id: ID группы
    name: Название группы (Текст любой длины)
    tag: Тэг группы для быстрого поиска (Текст длиной не более 64 символов)
    description: Описание группы (Текст любой длины)
    admins: Список Telegram ID администраторов группы
    users: Список Telegram ID пользователей группы
    invites: Список Telegram ID кому отправить приглашение в группу
    events: Список ID событий в группе
    """

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(String(64), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    admins: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="[]")
    users: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="[]")
    invites: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="[]")
    events: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="[]")


# Класс для хранения событий
class EventsModel(BaseModel):
    """
    id: ID события
    name: Название события (Текст любой длины)
    description: Описание события (Текст любой длины)
    date: Дата предстоящего события
    location: Локация события (URL ссылка на Яндекс Картах)
    users: Список Telegram ID пользователей, которые придут на событие
    invites: Список Telegram ID пользователей, кого приглашают на событие
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    date: Mapped[int] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    location: Mapped[str] = mapped_column(Text, nullable=True)
    users: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="[]")
    invites: Mapped[dict] = mapped_column(JSON, nullable=False, server_default="[]")
