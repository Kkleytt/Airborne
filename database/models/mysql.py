from database.models.base import Base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Text, Boolean, VARCHAR


class SettingsBase(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(VARCHAR(255), primary_key=True)
    type: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    tag: Mapped[str] = mapped_column(VARCHAR(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    editable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
