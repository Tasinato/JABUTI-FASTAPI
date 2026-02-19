from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from uuid import UUID

from src.schemas.user_schema import UserCreate, UserUpdate, UserResponse, UserListResponse 
from src.models.database import get_db
from src.models.user_model import User
from src.cache.redis_client import cache_get, cache_set, cache_delete, cache_delete_prefix


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


CACHE_TTL = 60


@router.get("/", response_model=UserListResponse)
async def list_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("nome"),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"usuarios:list:{limit}:{offset}:{sort}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    # total_count
    total_stmt = select(func.count()).select_from(User)
    total_count = (await db.execute(total_stmt)).scalar_one()

    allowed_sort_fields = {
        "nome": User.nome,
        "email": User.email,
        "idade": User.idade,
    }

    desc = sort.startswith("-")
    field = sort[1:] if desc else sort

    if field not in allowed_sort_fields:
        raise HTTPException(status_code=400, detail="Campo de ordenação inválido")

    order_column = allowed_sort_fields[field].desc() if desc else allowed_sort_fields[field]

    stmt = (
        select(User)
        .order_by(order_column)
        .limit(limit)
        .offset(offset)
    )

    users = (await db.execute(stmt)).scalars().all()

    page_number = (offset // limit) + 1
    has_next = (offset + limit) < total_count

    data = {
        "items": [UserResponse.model_validate(u).model_dump(mode="json") for u in users],
        "total_count": total_count,
        "has_next": has_next,
        "page_number": page_number,
    }

    await cache_set(cache_key, data, ttl=CACHE_TTL)

    return data




@router.get("/{id}", response_model=UserResponse)
async def get_user(id: UUID, db: AsyncSession = Depends(get_db)):
    cache_key = f"usuarios:id:{id}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return cached

    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    data = UserResponse.model_validate(user).model_dump(mode="json")
    await cache_set(cache_key, data, ttl=CACHE_TTL)
    
    return data


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    user = User(
        nome=payload.nome,
        email=payload.email,
        idade=payload.idade
    )

    db.add(user)

    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email já cadastrado"
        )
    
    await cache_delete_prefix("usuarios:list:")

    return user


@router.put("/{id}", response_model=UserResponse)
async def update_user(
    id: UUID,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    update_data = payload.model_dump(exclude_unset=True)

    # 🔎 valida email se estiver sendo alterado
    if "email" in update_data:
        stmt = select(User).where(
            User.email == update_data["email"],
            User.id != id
        )
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="Email já cadastrado"
            )

    # ✏️ aplica alterações dinamicamente
    for field, value in update_data.items():
        setattr(user, field, value)

    # 🔐 proteção contra race condition
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email já cadastrado"
        )

    await cache_delete_prefix("usuarios:list:")
    await cache_delete(f"usuarios:id:{id}")

    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: UUID, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    await db.delete(user)
    await db.commit()

    await cache_delete_prefix("usuarios:list:")
    await cache_delete(f"usuarios:id:{id}")
    
    return None
