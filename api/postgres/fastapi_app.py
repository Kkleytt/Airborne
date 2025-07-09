from fastapi import FastAPI, APIRouter, Request, Query, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
import uvicorn
import requests

from api.mysql.fastapi_app import get_url  # Получение URL API настроек
from database.models.postgresql import KnowledgeBaseModel, NewsBaseModel, UsersBaseModel, GroupsBaseModel, EventsBaseModel  # Схемы данных в PostgreSQL
from api.postgres.models import SettingResponse, SettingUpdate, SettingCreate  # Схемы запросов
from api.mysql.dependencies import get_mysql_client  # Зависимости с СУБД
from logger import sender as lg  # Логер


app = FastAPI()  # Создание FastApi приложения
router = APIRouter()  # Создание роутера
config = requests.get(f"{get_url()}/secret/many?tag=postgres").json()  # Получение настроек подключения


# Предоставление URL адреса для подключения
def get_url():
    return f"http://{config.get('pg_host')}:{config.get('pg_port')}"


if __name__ == "__main__":
    # Запуск API для общения с PostgreSQL
    uvicorn.run(
        app="api.postgres.fastapi_app:app",
        host=config.get('pg_host'),
        port=int(config.get('pg_port')),
        reload=True
    )
