import asyncio  # Асинхронный запуск функций
import json  # Работа с JSON строками
import aio_pika  # Асинхронный движок RabbitMq
import requests  # Отправка HTTP запросов

from settings.get_config import get_config  # Получение локального конфига
from api.mysql.fastapi_app import get_url  # Получение URL API настроек
from logger.methods.to_console import ConsoleLogger  # Вывод логов в консоль
from logger.methods.to_file import FileLogger  # Вывод логов в файл


# Создание данных для подключения к RabbitMq
config = get_config()['rabbitmq']
RABBITMQ_URL = f"amqp://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"


# Получение методов вывода логов (Консоль, Файл, БД)
def get_methods():
    response = requests.get(f"{get_url()}/secret/many?keys=log_save_method")
    response.raise_for_status()
    raw_data = response.json().get("log_save_method")

    if isinstance(raw_data, str):
        save_methods = json.loads(raw_data)
    elif isinstance(raw_data, dict):
        save_methods = raw_data
    else:
        save_methods = {}

    return [save_methods.get("console", True), save_methods.get("file", True), save_methods.get("db", True),]


save_to_console, save_to_file, save_to_database = get_methods()

# Создание объектов для записи логов
CONSOLE = ConsoleLogger()
FILE = FileLogger()


# Логика обработки логов
async def callback_logs(message: aio_pika.IncomingMessage):

    # Читаем сообщение с автоматическим удалением после чтения
    async with message.process():

        # Распаковка сообщения
        message = json.loads(message.body.decode())

        # Проверка на вывод логов в консоль
        if save_to_console is True:
            print(CONSOLE.format_log(message))

        # Проверка на сохранение логов в файл
        if save_to_file is True:
            FILE.log(message)


# Логика обработки Telegram запросов
async def callback_query(message: aio_pika.IncomingMessage):
    async with message.process():  # автоматическое подтверждение
        print(f"[LOG] {message.body.decode()}")


async def main():
    # Подключение к RabbitMQ
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    # Объявляем очередь (если не существует)
    logs_queue = await channel.declare_queue("logs", durable=True, auto_delete=False, arguments={"x-message-ttl": 30000})
    query_queue = await channel.declare_queue("query", durable=True, auto_delete=False, arguments={"x-message-ttl": 30000})

    # Подписываемся на сообщения
    await logs_queue.consume(callback_logs)
    await query_queue.consume(callback_query)

    # Бесконечное ожидание сообщений
    await asyncio.Future()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Выход из лог-консюмера.")
