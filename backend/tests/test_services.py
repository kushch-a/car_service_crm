import pytest
from fastapi import HTTPException
from databases import Database

# Імпортуємо те, що будемо тестувати
from crud.users import create_user
from schemas.users import UserCreate

# Позначаємо всі тести в цьому файлі як асинхронні
pytestmark = pytest.mark.asyncio


async def test_service_create_user_success(db_connection: Database):
    """
    Юніт-тест: успішне створення користувача на рівні сервісу.
    """
    # 1. Підготовка даних
    user_data = UserCreate(
        username="service_user",
        email="service@example.com",
        password="password123",
        role="manager"
    )

    # 2. Виклик функції
    created_user = await create_user(db_connection, user_data)

    # 3. Перевірка результату
    assert created_user is not None
    assert created_user.username == user_data.username
    assert created_user.email == user_data.email
    assert created_user.role == user_data.role
    assert created_user.id is not None


async def test_service_create_user_duplicate_username(db_connection: Database):
    """
    Юніт-тест: помилка при створенні користувача з існуючим іменем.
    """
    # 1. Підготовка: створюємо першого користувача
    user_data_1 = UserCreate(
        username="duplicate_user",
        email="duplicate1@example.com",
        password="password123",
        role="master"
    )
    await create_user(db_connection, user_data_1)

    # 2. Підготовка даних для другого (дублюючого) користувача
    user_data_2 = UserCreate(
        username="duplicate_user",  # Те саме ім'я
        email="duplicate2@example.com",
        password="password456",
        role="master"
    )

    # 3. Перевірка, що виклик функції з дублюючими даними генерує виключення
    with pytest.raises(HTTPException) as exc_info:
        await create_user(db_connection, user_data_2)

    # 4. Перевірка деталей виключення
    assert exc_info.value.status_code == 400
    assert "Username already registered" in exc_info.value.detail
