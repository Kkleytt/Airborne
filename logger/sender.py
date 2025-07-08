import json
import asyncio
import aio_pika
from datetime import datetime
from settings.get_config import get_config

# Глобальные объекты состояний
_connection = None  # Соединение с RabbitMQ
_channel = None     # Канал для работы
_initialized = False  # Статус инициализации
_log_queue = asyncio.Queue()  # Очередь логов
_worker_task = None  # Задача наблюдателя
_init_lock = asyncio.Lock()  # Блокировка для init
_ready_event = asyncio.Event()  # Статус запуска логера
_worker_started = asyncio.Event()  # Статус запуска наблюдателя


# Инициализация логера и запуск фонового наблюдателя
async def init_logger():
    global _connection, _channel, _initialized, _worker_task

    # Создание данных для подключения к RabbitMq
    config = get_config()['rabbitmq']
    rabbitmq_url = f"amqp://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"

    async with _init_lock:
        if _initialized:
            return
        try:
            _connection = await aio_pika.connect_robust(rabbitmq_url)  # Подключаемся к RabbitMQ
            _channel = await _connection.channel()  # Открываем канал

            # Создаем очередь для логов
            await _channel.declare_queue(
                "logs",
                durable=True,
                auto_delete=False,
                arguments={"x-message-ttl": 30000}  # Хранить до 30 секунд
            )

            _worker_task = asyncio.create_task(_log_worker())  # Создаём задачу для наблюдателя
            await _worker_started.wait()  # Ждём запуска наблюдателя

            _initialized = True
        except Exception as e:
            print(f"[Logger][ERROR] Не удалось подключиться к RabbitMQ: {e}")
            _initialized = False


# Фоновая проверка очереди логов и их отправка в RabbitMq
async def _log_worker():
    global _channel

    _worker_started.set()  # Сообщаем о запуске

    # Запускаем бесконечный цикл проверки очереди логов
    while True:

        log_entry = await _log_queue.get()  # Получаем запись из очереди
        try:
            # Публикуем лог в RabbitMQ
            await _channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(log_entry).encode()),
                routing_key="logs"
            )
        except Exception as e:
            print(f"[Logger][Worker ERROR] Не удалось отправить лог: {e}")
        finally:
            _log_queue.task_done()  # Отмечаем задание как выполненное


# Создание структуры лога
def _build_log(level: str, message: str, module: str = "None", code: int = 0) -> dict:
    # Формируем структуру лога
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level.upper(),
        "module": module.upper(),
        "message": message,
        "code": code
    }


# Создание асинхронной задачи на добавление лога в очередь
def _enqueue_log(level: str, message: str, module: str = "None", code: int = 0):
    asyncio.create_task(_safe_enqueue(level, message, module, code))


# Добавление лога в очередь
async def _safe_enqueue(level: str, message: str, module: str = "None", code: int = 0):

    # Проверка на запуск логера
    if not _initialized:
        await init_logger()
        await _ready_event.wait()  # Ожидание запуска

    log_entry = _build_log(level, message, module, code)  # Формируем запись лога
    await _log_queue.put(log_entry)  # Добавляем в очередь


# Информационное сообщение
def info(message: str, module: str = "None", code: int = 0):
    _enqueue_log("INFO", message, module, code)


# Предупреждающее сообщение
def warning(message: str, module: str = "None", code: int = 0):
    _enqueue_log("WARNING", message, module, code)


# Ошибочное сообщение
def error(message: str, module: str = "None", code: int = 1):
    _enqueue_log("ERROR", message, module, code)


# Критическое сообщение
def critical(message: str, module: str = "None", code: int = 2):
    _enqueue_log("CRITICAL", message, module, code)


# Неопознанное сообщение
def none(message: str, module: str = "None", code: int = 0):
    _enqueue_log("NONE", message, module, code)


# Закрытие соединения
async def close_logger():
    global _connection, _channel, _worker_task, _initialized
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task  # Ждём отмены задачи
        except asyncio.CancelledError:
            pass

    if _connection:
        try:
            await _connection.close()
        except Exception as e:
            print(f"[Logger] Ошибка при закрытии соединения: {e}")

    _initialized = False
    _worker_started.clear()


# Ожидание завершения всех логов
async def flush_logs():
    if not _initialized:
        await init_logger()
        await _ready_event.wait()

    await _log_queue.join()  # Ждём опустошения очереди
