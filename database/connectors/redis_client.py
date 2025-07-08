from typing import List, Dict, Any
import json
import redis.asyncio as redis


class Client:
    def __init__(self, host: str, port: int, password: str, database: str):
        self.host = host
        self.port = port

        self.password = password
        self.database = database

        self.redis_client = None
        self.connected = False

    async def connect(self):
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                password=self.password,
                db=int(self.database) if self.database.isdigit() else 0,
                decode_responses=True
            )
            self.connected = await self.redis_client.ping()
        except Exception as e:
            await self.handle_error(e)
            self.connected = False

    async def is_connected(self) -> bool:
        try:
            return await self.redis_client.ping()
        except Exception as ex:
            await self.handle_error(ex)
            return False

    async def execute(self, key: str, *args, **kwargs) -> List[Dict[str, Any]]:
        if not self.connected:
            await self.connect()
        try:
            value = await self.redis_client.get(key)
            if value:
                return [{"key": key, "value": json.loads(value)}]
            return []
        except Exception as e:
            await self.handle_error(e)
            return []

    @staticmethod
    async def handle_error(error: Exception) -> None:
        print(f"redis [ERROR] - {str(error)}")
