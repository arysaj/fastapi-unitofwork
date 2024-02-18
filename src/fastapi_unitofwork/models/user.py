from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime

from src.fastapi_unitofwork.models.basemodel import BaseModel


class UserModel(BaseModel):
    __tablename__ = "User"

    first_name: Mapped[str] = mapped_column(
        "FirstName", String(length=100), nullable=False
    )
    last_name: Mapped[str] = mapped_column(
        "LastName", String(length=100), nullable=False
    )
    email: Mapped[str] = mapped_column(
        "Email", String(length=255), nullable=False, unique=True, index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        "HashedPassword", String(length=1024), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        "IsActive", Boolean, default=True, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(
        "IsVerified", Boolean, default=False, nullable=False
    )
    verified_at: Mapped[datetime] = mapped_column(
        "VerifiedAt", DateTime, nullable=True, default=None
    )
