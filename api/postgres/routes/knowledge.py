from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError

from database.connectors.connector import get_client  # Подключение к PostgreSQL
from api.mysql.fastapi_app import get_url  # Получение url API настроек
import requests  # Отправка HTTP запросов

from database.models.postgresql import KnowledgeModel, UsersModel, NewsModel, GroupsModel, EventsModel  # Модель таблиц БД
from api.postgres.models import Knowledge  # Модели HTTP запросов


# Получение настроек подключения к Postgre
def get_connection_settings():
    data = requests.get(f"{get_url()}/secret/many?tag=postgres").json()
    return {
        "host": data.get("pg_host"),
        "port": int(data.get("pg_port")),
        "username": data.get("pg_username"),
        "password": data.get("pg_password"),
        "database": data.get("pg_database"),
    }


router = APIRouter()
config = get_connection_settings()
DB = get_client("postgres", **config)  # Подключение к БД


# Получение компонентов по ID, TAG, TYPE
@router.get("/knowledge", response_model=List[Knowledge.Response])
async def get_knowledge(id: Optional[int] = Query(None), tag: Optional[str] = Query(None), type_: Optional[str] = Query("text", alias="type")):
    filters = []

    if id:
        filters.append(KnowledgeModel.id == id)
    if tag:
        filters.append(KnowledgeModel.tag == tag)
    if type_:
        filters.append(KnowledgeModel.type == type_)

    results = await DB.select_model(
        model=KnowledgeModel,
        filters=and_(*filters) if filters else None
    )

    return results


@router.post("/knowledge", response_model=Knowledge.Response)
async def post_knowledge(payload: Knowledge.Create):
    try:
        result = await DB.insert_model(KnowledgeModel, payload.dict())
        return result
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid data")


@router.put("/knowldge", response_model=Knowledge.Response)
async def put_knowledge(id: str, payload: Knowledge.Update):
    # Проверка, что запись существует
    existing = await DB.select_model(KnowledgeModel, Knowledge.id == id, fetch_one=True)
    if not existing:
        raise HTTPException(status_code=404, detail="Record not found")

    # Проверка на разрешенные поля
    new_data = payload.dict(exclude_unset=True)
    if not new_data:
        raise HTTPException(status_code=400, detail="No valid fields provided")

    # Обновление записи
    await DB.update_fields(KnowledgeModel, {"id": id}, new_data)

    # Возврат обновлённой записи
    updated = await DB.select_model(KnowledgeModel, KnowledgeModel.id == id, fetch_one=True)
    return updated
