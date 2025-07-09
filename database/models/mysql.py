from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Text, Boolean, VARCHAR


# Класс для хранения настроек
class SettingsBase(DeclarativeBase):
    """
    key: Ключ для поиска параметров (Текст не более 64 символов)
    type: Тип параметра (INT, BOOL, STR, JSON, FLOAT) (Текст длиной не более 16 символов)
    value: Значение параметра (Любой текст, любой длины)
    tag: Тэг для группировки параметров (Текст длиной не более 64 символов)
    description: Описание параметра (Любой текст, любой длины)
    editable: Возможность изменения (True-поддается изменениям через API, False-не поддается изменениям)
    """

    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(VARCHAR(64), primary_key=True)
    type: Mapped[str] = mapped_column(VARCHAR(16), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(VARCHAR(64), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    editable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
