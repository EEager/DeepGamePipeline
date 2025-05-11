# services/db_writer.py
import aiomysql
import asyncio
import json

class DBWriter:
    def __init__(self, host="localhost", user="root", password="root", db="gamelogs"):
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.pool = None

    async def init_pool(self):
        self.pool = await aiomysql.create_pool(
            host=self.host, user=self.user, password=self.password, db=self.db, autocommit=True
        )

    async def write_log(self, event_type, details):
        if self.pool is None:
            await self.init_pool()
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "INSERT INTO logs (event_type, details) VALUES (%s, %s)",
                    (event_type, json.dumps(details))
                )

    async def close(self):
        if self.pool:
            self.pool.close()
            await self.pool.wait_closed()