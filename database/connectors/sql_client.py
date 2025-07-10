from typing import Optional, List, Dict, Any, Union, Type
from urllib.parse import quote_plus
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import select


class Client:
    def __init__(self, db_type: str, host: str, port: int, username: str, password: str, database: str):
        # Установка значений переменных
        self.db_type = db_type
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database

        # Служебные переменные
        self.connected = False
        self.engine = None
        self.async_session: Optional[sessionmaker] = None
        self._last_check: datetime = datetime.min
        self._reconnect_interval = timedelta(minutes=30)

    # Подключение к СУБД
    async def connect(self):
        try:

            # Преобразование пароля
            quoted_password = quote_plus(self.password)

            # Формирование строки подключения в зависимости от типа СУБД
            if self.db_type in ["postgres", "timescale"]:
                url = f"postgresql+asyncpg://{self.username}:{quoted_password}@{self.host}:{self.port}/{self.database}"
            elif self.db_type == "mysql":
                url = f"mysql+asyncmy://{self.username}:{quoted_password}@{self.host}:{self.port}/{self.database}"
            else:
                raise ValueError(f"Unsupported relational database type: {self.db_type}")

            # Инициализация асинхронного движка SQLAlchemy
            self.engine = create_async_engine(url, echo=False, pool_pre_ping=True)

            # Тест запроса на подключение
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))

            # Создание асинхронной сессии
            self.async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)
            self.connected = True
            self._last_check = datetime.now()
        except Exception as e:
            await self.handle_error(e)
            self.connected = False

    # Проверка подключения или переподключение при истечении таймера
    async def is_connected(self) -> bool:
        if not self.connected or datetime.now() - self._last_check > self._reconnect_interval:
            await self.connect()
        return self.connected

    # Создание таблицы модели, если она ещё не существует
    async def create_table_if_not_exists(self, model: Type):
        if not await self.is_connected():
            return
        try:
            async with self.engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: model.__table__.create(bind=sync_conn, checkfirst=True))
        except Exception as e:
            await self.handle_error(e)

    # Выполнение произвольного SQL-запроса
    async def execute(self, query: str, params: Optional[Union[Dict[str, Any], tuple]] = None, fetch_one: bool = False) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
        if not await self.is_connected():
            return []

        try:
            # Открытие сессии и выполнение запроса
            async with self.async_session() as session:
                result = await session.execute(text(query), params)
                keys = result.keys()
                rows = [dict(zip(keys, row)) for row in result]

                # Возвращаем либо одну запись, либо все
                return rows[0] if fetch_one and rows else (rows if rows else None)
        except Exception as e:
            await self.handle_error(e)
            return []

    # Вставка записи по переданным полям
    async def insert_model(self, model: Type, data: dict):
        # Если Бд - не подключена
        if not await self.is_connected():
            return

        try:
            async with self.async_session() as session:
                instance = model(**data)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)  # Обновляем данные из БД

                # Преобразуем ORM объект в словарь, исключая служебные атрибуты
                return {
                    k: v for k, v in vars(instance).items()
                    if not k.startswith("_")
                }
        except Exception as e:
            await self.handle_error(e)

    # Обновление записи по фильтру и новым данным
    async def update_fields(self, model: Type, filter_by: dict, new_data: dict):
        if not await self.is_connected():
            return
        try:
            async with self.async_session() as session:
                stmt = select(model).filter_by(**filter_by)
                result = await session.execute(stmt)
                instance = result.scalars().first()

                if not instance:
                    print(f"Запись не найдена для обновления: {filter_by}")
                    return

                for key, value in new_data.items():
                    setattr(instance, key, value)

                await session.commit()
        except Exception as e:
            await self.handle_error(e)

    # Выборка моделей из БД с фильтрацией (ORM)
    async def select_model(self, model: Type, filters: Optional[Any] = None, fetch_one: bool = False) -> List[Any]:
        if not await self.is_connected():
            return []
        try:
            # Открытие сессии и выполнение запроса
            async with self.async_session() as session:
                stmt = select(model)  # Создание запроса SELECT * FROM model WHERE filters

                # Добавляем фильтр при наличии
                if filters is not None:
                    stmt = stmt.where(filters)

                result = await session.execute(stmt)
                return result.scalars().first() if fetch_one else result.scalars().all()
        except Exception as e:
            await self.handle_error(e)
            return []

    # Обработка и вывод ошибок
    async def handle_error(self, error: Exception) -> None:
        print(f"{self.db_type} [ERROR] - {str(error)}")
