from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db import get_db
from src.app.dependencies.auth import get_current_user
from src.app.models import Address, User

router = APIRouter(prefix="/v1/addresses", tags=["addresses"])


class AddressCreate(BaseModel):
    title: Optional[str] = None
    recipient_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: str = "CN"
    is_default: bool = False


class AddressUpdate(BaseModel):
    title: Optional[str] = None
    recipient_name: Optional[str] = None
    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    id: int
    user_id: int
    title: Optional[str]
    recipient_name: Optional[str]
    phone: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    country: str
    is_default: bool
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}


@router.get("", response_model=List[AddressResponse])
async def list_addresses(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Address).where(Address.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    body: AddressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.is_default:
        await _clear_defaults(db, current_user.id)

    address = Address(
        user_id=current_user.id,
        title=body.title,
        recipient_name=body.recipient_name,
        phone=body.phone,
        address_line1=body.address_line1,
        address_line2=body.address_line2,
        city=body.city,
        province=body.province,
        postal_code=body.postal_code,
        country=body.country,
        is_default=body.is_default,
    )
    db.add(address)
    await db.flush()
    await db.refresh(address)
    return address


@router.put("/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    body: AddressUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id,
        )
    )
    address = result.scalar_one_or_none()
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    if body.is_default and body.is_default is not False:
        await _clear_defaults(db, current_user.id, exclude_id=address_id)

    update_data = body.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(address, key, value)

    await db.flush()
    await db.refresh(address)
    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Address).where(
            Address.id == address_id,
            Address.user_id == current_user.id,
        )
    )
    address = result.scalar_one_or_none()
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    await db.delete(address)
    await db.flush()


async def _clear_defaults(
    db: AsyncSession,
    user_id: int,
    exclude_id: Optional[int] = None,
):
    query = select(Address).where(
        Address.user_id == user_id,
        Address.is_default == True,
    )
    if exclude_id is not None:
        query = query.where(Address.id != exclude_id)

    result = await db.execute(query)
    for addr in result.scalars().all():
        addr.is_default = False
