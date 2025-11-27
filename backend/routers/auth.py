from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncConnection
from schemas.users import UserCreate, UserLogin, Token, UserInDB
from crud.users import create_user, get_user_by_username, verify_password
from auth.jwt import create_access_token
from db import get_db
from auth.deps import require_role

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/register", response_model=UserInDB)
async def register(
    user: UserCreate,
    db: AsyncConnection = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    existing = await get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    return await create_user(db, user)

@router.post("/login", response_model=Token)
async def login(user: UserLogin, db: AsyncConnection = Depends(get_db)):
    db_user = await get_user_by_username(db, user.username)
    if not db_user or not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    if not db_user["is_active"]:
        raise HTTPException(status_code=403, detail="User is inactive")
    token = create_access_token({"sub": db_user["username"], "role": db_user["role"]})
    return Token(access_token=token) 