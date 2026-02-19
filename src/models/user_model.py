import uuid
from sqlalchemy import Column, String, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from src.models.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    idade = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("idade >= 0", name="ck_users_idade_nonnegative"),
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
