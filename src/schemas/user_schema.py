from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=150)
    idade: int = Field(ge=0, strict=True)


class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    nome: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=150)
    idade: int | None = Field(default=None, ge=0, strict=True)

    @field_validator("nome", "email", "idade", mode="before")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("O campo não pode ser null; omita-o para manter o valor atual")
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str
    email: EmailStr
    idade: int


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total_count: int
    has_next: bool
    page_number: int
