import json
import asyncio
import aio_pika
from datetime import datetime, timezone
from settings.get_config import get_config


# Глобальное состояние
class LoggerState:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.initialized = False
        self.init_lock = asyncio.Lock()
        self.ready_event = asyncio.Event()
        self.log_queue = asyncio.Queue()
        self.query_queue = asyncio.Queue()
        self.worker_task = None


state = LoggerState()


# Инициализация подключения к RabbitMQ и запуск наблюдателя
async def init_logger():
    async with state.init_lock:
        if state.initialized:
            return

        config = get_config()['rabbitmq']
        url = f"amqp://{config['username']}:{config['password']}@{config['host']}:{config['port']}/"

        try:
            state.connection = await aio_pika.connect_robust(url)
            state.channel = await state.connection.channel()

            await state.channel.declare_queue("logs", durable=True, arguments={"x-message-ttl": 30000})
            await state.channel.declare_queue("queries", durable=True, arguments={"x-message-ttl": 30000})

            state.worker_task = asyncio.create_task(_worker())
            state.initialized = True
            state.ready_event.set()
        except Exception as e:
            print(f"[Logger][ERROR] Ошибка подключения к RabbitMQ: {e}")


# Универсальный наблюдатель для логов и запросов
async def _worker():
    while True:
        log_task = asyncio.create_task(state.log_queue.get())
        query_task = asyncio.create_task(state.query_queue.get())

        done, _ = await asyncio.wait(
            [log_task, query_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        if log_task in done:
            log_entry = log_task.result()
            try:
                await state.channel.default_exchange.publish(
                    aio_pika.Message(body=json.dumps(log_entry).encode()),
                    routing_key="logs"
                )
            except Exception as e:
                print(f"[Logger][Worker ERROR] Лог не отправлен: {e}")
            finally:
                state.log_queue.task_done()

        if query_task in done:
            query_entry = query_task.result()
            try:
                await state.channel.default_exchange.publish(
                    aio_pika.Message(body=json.dumps(query_entry).encode()),
                    routing_key="queries"
                )
            except Exception as e:
                print(f"[Logger][Worker ERROR] Запрос не отправлен: {e}")
            finally:
                state.query_queue.task_done()


# Формирование лог-сообщения
def _build_log(level: str, message: str, module: str = "None", code: int = 0):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level.upper(),
        "module": module.upper(),
        "message": message,
        "status_code": code
    }


# Формирование запроса
def _build_query(user_id: int, chat_id: int, text_type: str, text: str, time: int):
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "chat_id": chat_id,
        "query_type": text_type,
        "query_text": text,
        "response_time": time
    }


# Добавление в очередь лога
async def _safe_enqueue_log(level, message, module, code):
    if not state.initialized:
        await init_logger()
        await state.ready_event.wait()
    await state.log_queue.put(_build_log(level, message, module, code))


# Добавление в очередь запроса
async def _safe_enqueue_query(user_id, chat_id, text_type, text, time):
    if not state.initialized:
        await init_logger()
        await state.ready_event.wait()
    await state.query_queue.put(_build_query(user_id, chat_id, text_type, text, time))


# Публичные методы логирования
def info(message: str, module="None", code=0): asyncio.create_task(_safe_enqueue_log("INFO", message, module, code))
def warning(message: str, module="None", code=0): asyncio.create_task(_safe_enqueue_log("WARNING", message, module, code))
def error(message: str, module="None", code=1): asyncio.create_task(_safe_enqueue_log("ERROR", message, module, code))
def critical(message: str, module="None", code=2): asyncio.create_task(_safe_enqueue_log("CRITICAL", message, module, code))
def none(message: str, module="None", code=0): asyncio.create_task(_safe_enqueue_log("NONE", message, module, code))


# Публичный метод отправки Telegram-запроса
def query(user_id: int, chat_id: int, text_type: str, text: str, time: int):
    asyncio.create_task(_safe_enqueue_query(user_id, chat_id, text_type, text, time))


# Закрытие логера
async def close_logger():
    if state.worker_task:
        state.worker_task.cancel()
        try:
            await state.worker_task
        except asyncio.CancelledError:
            pass

    if state.connection:
        try:
            await state.connection.close()
        except Exception as e:
            print(f"[Logger] Ошибка при закрытии RabbitMQ: {e}")

    state.initialized = False
    state.ready_event.clear()


# Ожидание окончания всех задач
async def flush_logs():
    if not state.initialized:
        await init_logger()
        await state.ready_event.wait()

    await state.log_queue.join()
    await state.query_queue.join()
