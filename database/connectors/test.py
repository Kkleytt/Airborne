import asyncio
import aiohttp

from database.connectors.connector import get_client  # Клиент для подключения к СУБД
from database.models.mysql import SettingsBase  # Модель СУБД MySQL
from api.mysql.fastapi_app import get_url  # URL для общения с API
from logger import sender as lg  # Логер
from settings.get_config import get_config  # Получение локальных настроек


async def main():
    # ============================================================
    # Пример логирования данных в RabbitMq
    await lg.init_logger()  # Инициализация логера
    await asyncio.sleep(1)  # Задержка для завершения запуска логера

    # ============================================================
    # Пример подключения через ORM
    local_settings = get_config()
    config = {
        "db_type": "mysql",
        "host": local_settings['mysql']['host'],
        "port": local_settings['mysql']['port'],
        "username": local_settings['mysql']['username'],
        "password": local_settings['mysql']['password'],
        "database": local_settings['mysql']['database']
    }
    mysql_client = get_client(**config)  # Получение объекта СУБД
    await mysql_client.connect()  # Подключение к СУБД
    if await mysql_client.is_connected():
        lg.info(f"MySQL status connect - True")
    else:
        lg.error(f"MySQL status connect - False")

    # ============================================================
    # Пример создания таблицы используя ORM модель
    await mysql_client.create_table_if_not_exists(
        model=SettingsBase  # Модель для создания
    )

    # ============================================================
    # Пример добавления записи через ORM
    await mysql_client.insert_model(
        SettingsBase,  # Модель для применения полей
        # Данные для вставки
        {
            "key": "debug",
            "value": "true",
            "type": "bool",
            "tag": "system",
            "description": "Enable debug mode",
            "editable": True
        }
    )

    # ============================================================
    # Пример обновления записи через ORM
    await mysql_client.update_fields(
        model=SettingsBase,  # Выбор модели для применения полей
        filter_by={"key": "debug"},  # Выбор ключа для поиска записи и его значения
        new_data={"value": "false", "description": "Debug mode disabled", "editable": False}  # Новые данные для замены
    )

    # ============================================================
    # ORM-запрос через select_model() (Более удобный формат)
    settings = await mysql_client.select_model(
        model=SettingsBase,  # Модель для применения полей
        filters=SettingsBase.tag == 'postgres'  # Фильтр для применения
    )
    for item in settings:
        print(f"{item.key}: {item.value}")

    # ============================================================
    # ORM-запрос через execute() (Более гибкий формат)
    settings = await mysql_client.execute(
        query="SELECT * FROM settings WHERE tag = :tag",  # SQL запрос
        params={'tag': 'telegram'}  # Параметры для запроса
    )
    print(settings)

    # ============================================================
    # Пример подключения к СУБД через настройки из API
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{get_url()}/secret/many?tag=postgres') as response:
            pg_settings = await response.json()
    settings = {
        'db_type': 'postgres',
        'host': pg_settings['pg_host'],
        'port': pg_settings['pg_port'],
        'username': pg_settings['pg_username'],
        'password': pg_settings['pg_password'],
        'database': pg_settings['pg_database'],
    }
    postgres_client = get_client(**settings)
    await postgres_client.connect()
    print("PG Connected:", await postgres_client.is_connected())

    # ============================================================
    # Пример завершения работы логера (до-запись оставшихся логов)
    await lg.flush_logs()
    await lg.close_logger()
    print("Все логи отправлены и соединение закрыто!")


if __name__ == "__main__":
    asyncio.run(main())
