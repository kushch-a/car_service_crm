import os
from databases import Database
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

database = Database(DATABASE_URL)


# Викликається у FastAPI при старті/завершенні
async def connect_to_db():
    if not database.is_connected:
        await database.connect()


async def disconnect_from_db():
    if database.is_connected:
        await database.disconnect()


# Залежність для injection у ендпоінти
async def get_db() -> Database:
    return database
