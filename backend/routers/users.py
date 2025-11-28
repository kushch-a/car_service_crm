from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncConnection
from fastapi.responses import JSONResponse

from auth.deps import get_current_user
from db import get_db
from schemas.users import UserCreate, UserInDB, User, UserUpdate
from crud.users import create_user, get_all_users, get_user_by_id, update_user_in_db, delete_user_from_db
from shared_state import idem_store # Import from shared state

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/", response_model=list[UserInDB])
async def get_users(db: AsyncConnection = Depends(get_db)):
    return await get_all_users(db)

@router.post("/", response_model=UserInDB, status_code=201)
async def create_new_user(
    request: Request,
    user: UserCreate,
    db: AsyncConnection = Depends(get_db),
    idempotency_key: str = Header(None, alias="Idempotency-Key")
):
    """
    Створює нового користувача з підтримкою ідемпотентності.
    """
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="idempotency_key_required")

    if idempotency_key in idem_store:
        stored = idem_store[idempotency_key]
        return JSONResponse(content=stored["response"], status_code=stored["status"])

    try:
        new_user = await create_user(db, user)
        response_data = new_user.model_dump()
        status_code = 201

        idem_store[idempotency_key] = {"status": status_code, "response": response_data}
        
        return JSONResponse(content=response_data, status_code=status_code)

    except HTTPException as e:
        error_response = {
            "error": e.detail.lower().replace(" ", "_"),
            "details": e.detail,
            "request_id": getattr(request.state, "request_id", None)
        }
        status_code = e.status_code
        
        idem_store[idempotency_key] = {"status": status_code, "response": error_response}
        
        return JSONResponse(content=error_response, status_code=status_code)


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
        raise HTTPException(403, "permission_denied")
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
        raise HTTPException(403, "permission_denied")
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(404, "user_not_found")
    return await update_user_in_db(db, user_id, user_update)
