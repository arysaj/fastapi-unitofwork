from datetime import datetime

from sqlalchemy import Integer, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseModel(DeclarativeBase):
    id: Mapped[int] = mapped_column("Id", Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt", DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        "UpdatedAt",
        DateTime,
        server_default=func.now(),
        onupdate=datetime.now,
        nullable=True,
        default=None,
    )
