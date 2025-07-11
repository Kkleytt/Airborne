from fastapi import APIRouter, Query, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Literal
from pydantic import ValidationError
from pathlib import Path
import requests
import shutil
import os

from database.connectors.connector import get_client  # Подключение к PostgreSQL
from api.mysql.fastapi_app import get_url  # Получение url API настроек
from database.models.postgresql import KnowledgeModel  # Модель таблиц БД
from api.postgres.models import Knowledge  # Модели HTTP запросов
from logger import sender as lg  # Логер


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


router = APIRouter()  # Подключение роутера
config = get_connection_settings()  # Получение настроек подключения к БД
DB = get_client("postgres", **config)  # Подключение к БД


# Получение компонентов по ID, TAG, TYPE
@router.get("/knowledge", response_model=List[Knowledge.Response])
async def get_knowledge(
        id: Optional[int] = Query(None, description="ID записи для поиска"),
        tag: Optional[str] = Query(None, description="Тэг для поиска записи"),
        type_: Optional[str] = Query(None, alias="type", description="Тип записи для поиска")
):
    """
    Получение компонентов из БД с фильтрацией по полям

    :param id: ID компонента
    :param tag: Тэг для поиска компонентов
    :param type_: Тип компонента
    :return: Запись\Записи из БД
    """

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
            lg.info(f"Не существует записи с данными фильтрами: id={id}, tag={tag}, type={type_}", module="KnowledgeAPI")
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
    """
    Создание нового компонента

    :param payload: Данные компонента
    :return: Запись из БД с ID нового компонента
    """

    try:
        result = await DB.insert_model(KnowledgeModel, payload.dict())
        return result
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Некорректные данные")

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
async def put_knowledge(
        payload: Knowledge.Update,
        id: int = Query(None, description="ID компонента для обновления")
):
    """
    Обновление компонента в БД

    :param payload: Данные для изменения компонента
    :param id: ID компонента для применения новых данных
    :return: Запись из БД с обновленными данными
    """

    try:
        # Проверка, что запись существует
        existing = await DB.select_model(KnowledgeModel, KnowledgeModel.id == id, fetch_one=True)
        if not existing:
            raise HTTPException(status_code=204, detail="Record not found")

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
async def upload_file(
        file: UploadFile = File(...),
        name: str = Form(...),
        tag: str = Form(...),
        description: str = Form(...),
        creator_id: int = Form(...)
):
    """
    Сохранение файла в базе знаний.

    :param file: Загруженный файл или изображение
    :param name: Предпочитаемое имя файла
    :param tag: Тэг для записи
    :param description: Описание файла
    :param creator_id: Telegram ID создателя записи
    :return: Запись из БД с ID файла
    """

    # Детектор типа файла по его расширению
    def detect_file_type(extension: str) -> Literal["image", "video", "audio", "document", "text", "unknown"]:
        if extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
            return "image"
        elif extension in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
            return "video"
        elif extension in [".mp3", ".wav", ".aac", ".ogg", ".flac"]:
            return "audio"
        elif extension in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]:
            return "document"
        elif extension in [".txt", ".md", ".csv", ".log"]:
            return "text"
        else:
            return "unknown"

    try:
        # Путь сохранения
        safe_name = name.replace(" ", "_")  # Преобразование названия файла
        ext = os.path.splitext(file.filename)[-1]   # Получение расширения файла
        file_type = detect_file_type(ext)   # Определение типа файла
        save_path = Path(f"storage/files/{file_type}/{safe_name}{ext}")  # Создание пути сохранения
        save_path.parent.mkdir(parents=True, exist_ok=True)  # Создание директорий в пути сохранения

        # Сохранение файла
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Добавление записи в БД
        data = {
            "editor": creator_id,
            "type": file_type,
            "tag": tag,
            "description": description,
            "value": f"{safe_name}{ext}"
        }
        return await DB.insert_model(KnowledgeModel, data)

    except HTTPException as http_exc:
        raise http_exc


# Получение файла или изображения
@router.get("/knowledge/file")
async def get_knowledge_file(
        id: int = Query(..., description="ID файла для получения")
):
    """
    Получение файлов по ID записи в базе знаний.

    :param id: Уникальный идентификатор записи с файлом
    :return: Файл в виде HTTP-ответа
    """

    try:
        # Поиск записи по ID
        record = await DB.select_model(
            KnowledgeModel,
            KnowledgeModel.id == id,
            fetch_one=True
        )

        # Проверка, что запись с таким ID существует
        if not record:
            lg.warning(f"Запись с id={id} не найдена", module="KnowledgeAPI")
            raise HTTPException(status_code=404, detail="Записи с таким ID не существует")

        # Проверка, что запись является файлом
        if record.type not in ["file", "document", "image", "audio", "video"]:
            lg.warning(f"Запись с id={id} не является файлом", module="KnowledgeAPI")
            raise HTTPException(status_code=404, detail="Запись не является файлом")

        # Генерация пути до файла
        file_path = f"storage/files/{record.type}/{record.value}"

        # Возвращаем файл как ответ
        return FileResponse(path=file_path, filename=record.value)

    except HTTPException as http_exc:
        raise http_exc

    except SQLAlchemyError as sa_err:
        lg.error(f"Ошибка базы данных при получении файла id={id}: {str(sa_err)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Ошибка при получении файла из базы данных")

    except Exception as e:
        lg.error(f"Неизвестная ошибка при получении файла id={id}: {str(e)}", module="KnowledgeAPI")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")
