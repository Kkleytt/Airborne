from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Integer, Text, TIMESTAMP, BigInteger, String
from sqlalchemy.sql import func


# Класс для хранения логов
class LogsBase(DeclarativeBase):
    """
    id: ID лога
    timestamp: Время записи лога
    level: Уровень логирования (INFO, WARNING, ERROR, CRITICAL, NONE) (Текст длиной не более 16 символов)
    module: Модуль от которого пришел лог (Текст длиной не более 64 символов)
    message: Сообщение лога (Текст любой длины)
    code: Код ошибки
    """

    __tablename__ = "logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    level: Mapped[str] = mapped_column(String(16), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)


# Класс для хранения Telegram запросов
class QueryBase(DeclarativeBase):
    """
    id: ID запроса
    timestamp: Timestamp дата прихода запроса
    user_id: Telegram ID пользователя
    chat_id: Telegram ID чата
    query_type: Типа запроса (callback, message, command) (Текст длиной не более 32 символов)
    query_text: Текст запроса (Текст любой длины)
    response_time: Время обработки запроса в миллисекундах
    status_code: Код ответа пользователю
    """

    __tablename__ = "telegram_query"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    query_type: Mapped[str] = mapped_column(String(32), nullable=False)
    query_text: Mapped[str] = mapped_column(Text, nullable=False)
    response_time: Mapped[int] = mapped_column(Integer, nullable=True)
    status_code: Mapped[int] = mapped_column(Integer, nullable=True)
