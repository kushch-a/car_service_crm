import time
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from passlib.context import CryptContext

from db import connect_to_db, disconnect_from_db
from routers import customers, cars, services, auth, invoices, invoice_items, users
from shared_state import rate_limit_store

# --- Constants ---
# Змінено для зручності розробки
WINDOW_MS = 2000  # 2 секунди
MAX_REQUESTS = 30 # 30 запитів

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    from db import database
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    query = "SELECT id FROM users WHERE username = :username"
    result = await database.fetch_one(query, {"username": "admin"})
    if not result:
        password_hash = pwd_context.hash("admin123")
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
    
    yield
    
    await disconnect_from_db()

app = FastAPI(
    title="CRM для СТО",
    description="Простий FastAPI-проєкт для керування клієнтами, авто і послугами",
    version="1.0.0",
    lifespan=lifespan
)

# --- Middleware ---

@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    ip = request.client.host
    current_time = time.time()
    
    if ip not in rate_limit_store:
        rate_limit_store[ip] = {"count": 1, "timestamp": current_time}
    else:
        data = rate_limit_store[ip]
        if current_time - data["timestamp"] > WINDOW_MS / 1000:
            data["count"] = 1
            data["timestamp"] = current_time
        else:
            data["count"] += 1

    if rate_limit_store[ip]["count"] > MAX_REQUESTS:
        response = JSONResponse(
            status_code=429,
            content={
                "error": "too_many_requests",
                "details": "Rate limit exceeded. Please try again later.",
                "request_id": getattr(request.state, "request_id", None)
            }
        )
        response.headers["Retry-After"] = str(int(WINDOW_MS / 1000))
        return response
        
    response = await call_next(request)
    return response

# --- Обробник помилок ---

@app.exception_handler(Exception)
async def unified_error_handler(request: Request, exc: Exception):
    status_code = 500
    error_code = "internal_server_error"
    details = "An unexpected error occurred."

    if isinstance(exc, HTTPException):
        status_code = exc.status_code
        details = exc.detail
        if isinstance(details, str) and " " not in details:
            error_code = details.lower().replace(" ", "_")
        else:
            error_code = "http_exception"

    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_code,
            "details": details,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

# Middleware — CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення роутерів
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

@app.get("/health")
async def health_check():
    return {"status": "ok"}
