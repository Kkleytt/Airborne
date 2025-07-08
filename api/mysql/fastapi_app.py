from fastapi import FastAPI, APIRouter, Request, Query, Depends, HTTPException
from typing import List, Dict
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_
import uvicorn

from settings.get_config import get_config
from database.models.mysql import SettingsBase
from api.mysql.models import SettingResponse, SettingUpdate, SettingCreate
from api.mysql.dependencies import get_mysql_client
from logger import sender as lg


app = FastAPI()  # Создание FastApi приложения
config = get_config()  # Получение локальных настроек


# Предоставление URL адреса для подключения
def get_url():
    return f"http://{config['api']['host']}:{config['api']['port']}"


# Логирование запроса
@app.middleware("http")
async def log_requests(request: Request, call_next):

    # Получаем данные клиента
    client_host = request.client.host if request.client else "unknown"
    client_port = request.client.port

    # Обрабатываем запрос
    response = await call_next(request)

    # Собираем лог для передачи
    module = "fastapi-settings"
    message = f"{request.method} {request.url.path}?{request.url.query} from {client_host}:{client_port}"
    code = response.status_code

    # Логируем завершение запроса
    match code:
        case 200:
            lg.info(message, module, code)
        case _:
            lg.warning(message, module, code)

    return response


# Получение настроек с поиском по key, tag, type, editable
@app.get("/secret", response_model=List[SettingResponse])
async def get_settings(key: str = Query(None), tag: str = Query(None), value_type: str = Query(None), editable: bool = Query(None), db=Depends(get_mysql_client)):
    filters = []

    # Добавляем параметры в фильтрацию
    if key is not None:
        filters.append(SettingsBase.key == key)
    if tag is not None:
        filters.append(SettingsBase.tag == tag)
    if value_type is not None:
        filters.append(SettingsBase.type == value_type)
    if editable is not None:
        filters.append(SettingsBase.editable == editable)

    result = await db.select_model(
        model=SettingsBase,
        filters=and_(*filters) if filters else None
    )
    return result


# Получение множества значений ключей
@app.get("/secret/many", response_model=Dict[str, str])
async def get_list_settings(keys: List[str] = Query(None), tag: str = Query(None), db=Depends(get_mysql_client)):
    filters = []

    if keys:
        filters.append(SettingsBase.key.in_(keys))
    if tag:
        filters.append(SettingsBase.tag == tag)

    if not filters:
        return {}

    results = await db.select_model(
        model=SettingsBase,
        filters=or_(*filters)
    )

    return {setting.key: setting.value for setting in results}


# Добавление новых настроек
@app.post("/secret", response_model=SettingResponse)
async def create_setting(payload: SettingCreate, db=Depends(get_mysql_client)):
    # Проверка, есть ли уже такая настройка
    existing = await db.select_model(SettingsBase, SettingsBase.key == payload.key, fetch_one=True)
    if existing:
        raise HTTPException(status_code=409, detail="Setting with this key already exists")

    try:
        await db.insert_model(SettingsBase, payload.dict())
        return payload
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Invalid data")


# Обновление настроек с поиском по ключу
@app.put("/secret/{key}", response_model=SettingResponse)
async def update_setting(key: str, payload: SettingUpdate, db=Depends(get_mysql_client)):
    # Проверка, что запись существует
    existing = await db.select_model(SettingsBase, SettingsBase.key == key, fetch_one=True)
    if not existing:
        raise HTTPException(status_code=404, detail="Setting not found")

    # Проверка, что запись поддается изменения
    if existing.editable is False:
        raise HTTPException(status_code=400, detail="No change this secret")

    # Проверка на разрешенные поля
    new_data = payload.dict(exclude_unset=True)
    if not new_data:
        raise HTTPException(status_code=400, detail="No valid fields provided")

    # Обновление записи
    await db.update_fields(SettingsBase, {"key": key}, new_data)

    # Возврат обновлённой записи
    updated = await db.select_model(SettingsBase, SettingsBase.key == key, fetch_one=True)
    return updated


if __name__ == "__main__":
    # Запуск API для общения с MySQL
    uvicorn.run(
        app="api.mysql.fastapi_app:app",
        host=config['api']['host'],
        port=int(config['api']['port']),
        reload=True
    )
