from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Form
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Literal
from pydantic import ValidationError
from sqlalchemy import and_
from pathlib import Path
import shutil
import os
import requests

from database.connectors.connector import get_client  # Подключение к PostgreSQL
from api.mysql.fastapi_app import get_url  # Получение url API настроек
from database.models.postgresql import KnowledgeModel  # Модель таблиц БД
from api.postgres.models import Knowledge  # Модели HTTP запросов
from logger import sender as lg


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


def detect_file_type(filename: str) -> Literal["image", "video", "audio", "document", "text", "unknown"]:
    ext = os.path.splitext(filename)[1].lower()  # Получаем расширение (с точкой)

    if ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
        return "image"
    elif ext in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
        return "video"
    elif ext in [".mp3", ".wav", ".aac", ".ogg", ".flac"]:
        return "audio"
    elif ext in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]:
        return "document"
    elif ext in [".txt", ".md", ".csv", ".log"]:
        return "text"
    else:
        return "unknown"


router = APIRouter()
config = get_connection_settings()
DB = get_client("postgres", **config)  # Подключение к БД


# Получение компонентов по ID, TAG, TYPE
@router.get("/knowledge", response_model=List[Knowledge.Response])
async def get_knowledge(id: Optional[int] = Query(None), tag: Optional[str] = Query(None), type_: Optional[str] = Query("text", alias="type")):
    try:
        filters = []

        # Добавление фильтров к запросу
        if id:
            filters.append(KnowledgeModel.id == id)
        if tag:
            filters.append(KnowledgeModel.tag == tag)
        if type_:
            filters.append(KnowledgeModel.type == type_)

        # Отправка запроса к БД
        results = await DB.select_model(
            model=KnowledgeModel,
            filters=and_(*filters) if filters else None
        )

        # Логируем ситуацию, когда результатов нет
        if not results:
            lg.info(f"Knowledge entries not found with filters: id={id}, tag={tag}, type={type_}", module="KnowledgeAPI")
            raise HTTPException(status_code=404, detail="Записи не найдены")

        return results

    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError as sa_err:
        lg.error(f"Ошибка базы данных при получении knowledge: {str(sa_err)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера: ошибка базы данных")

    except Exception as e:
        lg.error(f"Неизвестная ошибка при получении knowledge: {str(e)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# Добавление нового компонента (текст, клавиатура, файлы, изображения)
@router.post("/knowledge", response_model=Knowledge.Response)
async def post_knowledge(payload: Knowledge.Create):
    try:
        result = await DB.insert_model(KnowledgeModel, payload.dict())
        return result
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid data")

    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError as sa_err:
        lg.error(f"Ошибка базы данных при получении knowledge: {str(sa_err)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера: ошибка базы данных")

    except Exception as e:
        lg.error(f"Неизвестная ошибка при получении knowledge: {str(e)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# Обновление компонента
@router.put("/knowledge", response_model=Knowledge.Response)
async def put_knowledge(id: int, payload: Knowledge.Update):
    try:
        # Проверка, что запись существует
        existing = await DB.select_model(KnowledgeModel, KnowledgeModel.id == id, fetch_one=True)
        if not existing:
            raise HTTPException(status_code=404, detail="Record not found")

        # Проверка на разрешенные поля
        new_data = payload.dict(exclude_unset=True)
        if not new_data:
            raise HTTPException(status_code=400, detail="No valid fields provided")

        # Обновление записи и возврат новой записи
        return await DB.update_fields(KnowledgeModel, {"id": id}, new_data)

    except HTTPException as http_exc:
        raise http_exc  # Пробрасываем стандартные ошибки дальше

    except ValidationError as ve:
        lg.error(f"Ошибка валидации данных: {ve.json()}", module="KnowledgeAPI")
        raise HTTPException(status_code=422, detail="Ошибка валидации входных данных")

    except SQLAlchemyError as sa_err:
        lg.error(f"Ошибка базы данных при обновлении knowledge: {str(sa_err)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера: ошибка базы данных")

    except Exception as e:
        lg.error(f"Неизвестная ошибка при обновлении knowledge: {str(e)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# Загрузка файла или изображения
@router.post("/knowledge/file", response_model=Knowledge.Response)
async def upload_file(file: UploadFile = File(...), name: str = Form(...), tag: str = Form(...), description: str = Form(...), creator_id: int = Form(...)):
    try:
        # Определение типа файла по содержимому
        file_type = detect_file_type(file.filename)

        # Путь сохранения
        safe_name = name.replace(" ", "_")
        ext = os.path.splitext(file.filename)[-1]
        save_path = Path(f"storage/files/{file_type}/{safe_name}{ext}")
        save_path.parent.mkdir(parents=True, exist_ok=True)

        # Сохранение файла
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Ответ на запрос и добавление записи в БД
        data = {
            "editor": creator_id,
            "type": file_type,
            "tag": tag,
            "description": description,
            "value": f"{safe_name}{ext}"
        }
        return await DB.insert_model(KnowledgeModel, data)

    except HTTPException:
        raise HTTPException(status_code=500, detail="Error processing file")
