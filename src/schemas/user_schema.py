from pydantic import BaseModel, EmailStr, Field

from uuid import UUID
from typing import List

class UserCreate(BaseModel):
    nome: str = Field(min_length=1)
    email: EmailStr
    idade: int = Field(ge=0)


class UserResponse(BaseModel):
    id: UUID
    nome: str
    email: EmailStr
    idade: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1)
    email: EmailStr | None = None
    idade: int | None = Field(default=None, ge=0)


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total_count: int
    has_next: bool
    page_number: int

    class Config:
        from_attributes = True