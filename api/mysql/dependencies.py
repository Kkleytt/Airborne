from database.connectors.connector import get_client
from settings.get_config import get_config

config = get_config()


# Получение MySQL клиента
async def get_mysql_client():
    try:
        client = get_client(
            db_type="mysql",
            host=config["mysql"]["host"],
            port=config["mysql"]["port"],
            username=config["mysql"]["username"],
            password=config["mysql"]["password"],
            database=config["mysql"]["database"]
        )
        await client.connect()
        print("[MySQL Client] Подключение успешно")
        return client
    except Exception as e:
        print("[MySQL Client ERROR]", e)
        raise e
