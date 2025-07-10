from fastapi import FastAPI, Request
import uvicorn
import requests

from api.mysql.fastapi_app import get_url  # Получение URL API настроек
from logger import sender as lg  # Логер
from api.postgres.routes import knowledge


def get_api_settings():
    data = requests.get(f"{get_url()}/secret/many?tag=api").json()
    return {
        "host": data.get("api_host"),
        "port": int(data.get("api_port"))
    }


app = FastAPI()  # Создание FastApi приложения
app.include_router(knowledge.router)  # Присоединение путей запросов

config = get_api_settings()  # Получение настроек API


# Предоставление URL адреса для подключения
def get_url():
    return f"http://{config.get('host')}:{config.get('port')}"


# Логирование запроса
@app.middleware("http")
async def log_requests(request: Request, call_next):

    # Получаем данные клиента
    client_host = request.client.host if request.client else "unknown"
    client_port = request.client.port

    # Обрабатываем запрос
    response = await call_next(request)

    # Собираем лог для передачи
    module = "fastapi-postgres"
    message = f"{request.method} {request.url.path}?{request.url.query} from {client_host}:{client_port}"
    code = response.status_code

    # Логируем завершение запроса
    match code:
        case 200:
            lg.info(message, module, code)
        case _:
            lg.warning(message, module, code)

    return response


if __name__ == "__main__":
    # Запуск API для общения с PostgreSQL
    uvicorn.run(
        app="api.postgres.fastapi_app:app",
        host=config.get("host"),
        port=config.get("port"),
        reload=True
    )
