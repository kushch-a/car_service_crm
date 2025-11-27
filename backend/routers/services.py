from fastapi import APIRouter, Depends, HTTPException
from schemas.services import ServiceCreate, ServiceUpdate, ServiceInDB
from typing import List
from db import get_db
from crud.services import (
    get_all_services,
    get_service_by_id,
    create_service,
    update_service,
    delete_service,
    delete_service_from_db,
)
from databases import Database
from schemas.users import User
from crud.users import get_current_user
from sqlalchemy.ext.asyncio import AsyncConnection

router = APIRouter(
    prefix="/services",
    tags=["Services"]
)

@router.get("/", response_model=List[ServiceInDB])
async def read_services(db: Database = Depends(get_db)):
    return await get_all_services(db)


@router.get("/{service_id}", response_model=ServiceInDB)
async def read_service(service_id: int, db: Database = Depends(get_db)):
    service = await get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


@router.post("/", response_model=ServiceInDB, status_code=201)
async def create_new_service(service: ServiceCreate, db: Database = Depends(get_db)):
    return await create_service(db, service)


@router.put("/{service_id}", response_model=ServiceInDB)
async def update_existing_service(service_id: int, service: ServiceUpdate, db: Database = Depends(get_db)):
    updated = await update_service(db, service_id, service)
    if not updated:
        raise HTTPException(status_code=404, detail="Service not found")
    return updated


@router.delete("/{service_id}", status_code=204)
async def delete_service(
    service_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(403, "Тільки адмін або менеджер може видаляти послуги")
    await delete_service_from_db(db, service_id)
    return


@router.patch("/{service_id}", response_model=ServiceInDB)
async def update_service_endpoint(
    service_id: int,
    service_update: ServiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncConnection = Depends(get_db)
):
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(403, "Тільки адмін або менеджер може редагувати послуги")
    service = await get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(404, "Послугу не знайдено")
    print("service_update:", service_update)
    print("service_update.dict():", service_update.dict())
    return await update_service(db, service_id, service_update)
