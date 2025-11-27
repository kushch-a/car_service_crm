from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncConnection
from auth.deps import get_current_user
from db import get_db
from schemas.users import UserCreate, UserInDB, User, UserUpdate
from crud.users import create_user, get_all_users, get_current_user, get_user_by_id, update_user_in_db, delete_user_from_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/", response_model=list[UserInDB])
async def get_users(db: AsyncConnection = Depends(get_db)):
    return await get_all_users(db)

@router.post("/", response_model=UserInDB)
async def create_new_user(user: UserCreate, db: AsyncConnection = Depends(get_db)):
    return await create_user(db, user)

@router.get("/me")
async def read_me(current_user=Depends(get_current_user)):
    return current_user

@router.get("/user", response_model=User)
async def get_user(current_user: User = Depends(get_current_user)):
    return current_user

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Тільки адмін може видаляти користувачів")
    await delete_user_from_db(db, user_id)
    return 

@router.patch("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(403, "Тільки адмін може редагувати користувачів")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "Користувача не знайдено")
    return await update_user_in_db(db, user_id, user_update) 