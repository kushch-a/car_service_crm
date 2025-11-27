from schemas.users import UserCreate, UserInDB
from sqlalchemy.ext.asyncio import AsyncConnection
from passlib.context import CryptContext
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime
from auth.jwt import SECRET_KEY, ALGORITHM
from db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

async def create_user(db: AsyncConnection, user: UserCreate) -> UserInDB:
    # Перевірка на існування користувача
    existing_user = await get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Можна додати і перевірку email, якщо потрібно
    # query_email = "SELECT id FROM users WHERE email = :email"
    # existing_email = await db.fetch_one(query_email, {"email": user.email})
    # if existing_email:
    #     raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    query = """
        INSERT INTO users (username, email, role, password_hash, created_at, updated_at)
        VALUES (:username, :email, :role, :password_hash, now(), now())
        RETURNING id, username, email, role, is_active, created_at, updated_at, password_hash
    """
    row = await db.fetch_one(query, {
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "password_hash": hashed_password,
    })
    return UserInDB(**dict(row))

async def get_user_by_username(db: AsyncConnection, username: str) -> Optional[UserInDB]:
    query = """
        SELECT id, username, email, password_hash, role, is_active
        FROM users
        WHERE username = :username
    """
    row = await db.fetch_one(query, {"username": username})
    if row:
        return dict(row)
    return None

async def get_user_by_id(db: AsyncConnection, user_id: int) -> Optional[UserInDB]:
    query = """
        SELECT id, username, email, role, is_active, created_at, updated_at, password_hash
        FROM users
        WHERE id = :user_id
    """
    row = await db.fetch_one(query, {"user_id": user_id})
    if row:
        return UserInDB(**dict(row))
    return None

async def get_all_users(db: AsyncConnection):
    query = """
        SELECT id, username, email, role, is_active, created_at, updated_at, password_hash
        FROM users
        ORDER BY id
    """
    rows = await db.fetch_all(query)
    return [UserInDB(**dict(row)) for row in rows]

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncConnection = Depends(get_db)
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return UserInDB(**user)

async def update_user_in_db(db, user_id: int, user_update):
    fields = []
    params = {"user_id": user_id}
    for key, value in user_update.dict(exclude_unset=True).items():
        fields.append(f"{key} = :{key}")
        params[key] = value
    if not fields:
        return None
    query = f"""
        UPDATE users SET {', '.join(fields)}
        WHERE id = :user_id
        RETURNING id, username, email, role, is_active, created_at, updated_at, password_hash
    """
    row = await db.fetch_one(query, params)
    if row:
        from schemas.users import UserInDB
        return UserInDB(**dict(row))
    return None

async def delete_user_from_db(db, user_id: int):
    query = "DELETE FROM users WHERE id = :user_id"
    await db.execute(query, {"user_id": user_id})