import pytest
from fastapi.testclient import TestClient
import asyncio
from databases import Database
import os

# Завантажуємо змінні середовища для доступу до DATABASE_URL
from dotenv import load_dotenv
load_dotenv()

# Додаємо шлях до backend, щоб можна було імпортувати main
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app

DATABASE_URL = os.getenv("DATABASE_URL")

# Читаємо SQL для ініціалізації
sql_file_path = os.path.join(os.path.dirname(__file__), '../../init_db.sql')
with open(sql_file_path, "r") as f:
    init_sql = f.read()

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """
    Автоматично очищує та створює таблиці перед кожним тестом.
    """
    async def _setup_database():
        database = Database(DATABASE_URL)
        await database.connect()
        try:
            for statement in init_sql.split(';'):
                if statement.strip():
                    await database.execute(statement)
        finally:
            await database.disconnect()
    asyncio.run(_setup_database())

@pytest.fixture(scope="function")
async def db_connection():
    """
    Надає асинхронне підключення до бази даних для юніт-тестів.
    """
    database = Database(DATABASE_URL)
    await database.connect()
    try:
        yield database
    finally:
        await database.disconnect()

@pytest.fixture(scope="function")
def client():
    """
    Надає клієнт для тестування API.
    """
    with TestClient(app) as c:
        yield c
