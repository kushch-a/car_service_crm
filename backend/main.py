from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext

from db import connect_to_db, disconnect_from_db

from routers import customers, cars, services, auth, invoices, invoice_items, users


SECRET_KEY = "qwerty1234567890"  
ALGORITHM = "HS256"
app = FastAPI(
    title="CRM для СТО",
    description="Простий FastAPI-проєкт для керування клієнтами, авто і послугами",
    version="1.0.0"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Підключення до бази
@app.on_event("startup")
async def startup(): 
    await connect_to_db()
    # --- Додаємо автододавання адміна ---
    from db import database  # або твій спосіб отримати db
    query = """
        SELECT id, username, email, role, is_active, created_at, updated_at, password_hash
        FROM users WHERE username = :username
    """
    result = await database.fetch_one(query, {"username": "admin"})
    if not result:
        password_hash = pwd_context.hash("admin123")  # пароль для адміна
        await database.execute(
            "INSERT INTO users (username, email, role, is_active, password_hash) VALUES (:username, :email, :role, :is_active, :password_hash)",
            {
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin",
                "is_active": True,
                "password_hash": password_hash,
            }
        )
        print(">>> Створено дефолтного адміна: admin/admin123")

@app.on_event("shutdown")
async def shutdown():
    await disconnect_from_db()

# Middleware — дозволимо фронтенду підключатись
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # у проді тут будуть точні домени
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутерів
app.include_router(customers.router)
app.include_router(customers.router)
app.include_router(cars.router)
app.include_router(services.router)
app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(invoice_items.router)
app.include_router(users.router)
# Головна перевірка API
@app.get("/")
async def root():
    return {"message": "CRM API is running"}

