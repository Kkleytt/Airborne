from database.connectors.sql_client import Client as SqlClient
from database.connectors.redis_client import Client as RedisClient


def get_client(db_type: str, host: str, port: int, username: str, password: str, database: str):
    """
    :param db_type: Тип СУБД
    :param host: Хост для подключения
    :param port: Порт для подключения
    :param username: Логин для подключения
    :param password: Пароль для подключения
    :param database: База Данных для подключения
    :return: Client
    """

    # Подключение к SQL базам данных
    if db_type in ["postgres", "mysql", "timescale"]:
        return SqlClient(db_type, host, port, username, password, database)

    # Подключение к Redis
    elif db_type == "redis":
        return RedisClient(host, port, username, password, database)

    # Обработка неверного типа СУБД
    else:
        raise ValueError(f"Данный тип БД не поддерживается: {db_type}")
