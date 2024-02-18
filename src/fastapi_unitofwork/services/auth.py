from datetime import timedelta, datetime, timezone

import jwt
from passlib.context import CryptContext

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import ValidationError

from src.fastapi_unitofwork.configs.settings import get_settings
from src.fastapi_unitofwork.services.uow import UnitOfWorkBase
from src.fastapi_unitofwork.schemas.token import TokenSchema
from src.fastapi_unitofwork.models.user import UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)
settings = get_settings()


class AuthService:
    @classmethod
    def _verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def _get_password_hash(cls, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    def _create_token(cls, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )
        return encoded_jwt

    @classmethod
    def _get_user_token(cls, user: UserModel, scopes: list) -> TokenSchema:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = cls._create_token(
            data={"sub": user.email, "scopes": scopes},
            expires_delta=access_token_expires,
        )

        refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token = cls._create_token(
            data={"sub": user.email}, expires_delta=refresh_token_expires
        )

        return TokenSchema(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @classmethod
    async def login_for_access_token(
        cls, uow: UnitOfWorkBase, form_data: OAuth2PasswordRequestForm
    ) -> TokenSchema:
        async with uow:
            exception = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

            user_orm = await uow.users.get_by_email(form_data.username)
            if not user_orm:
                raise exception

            if not cls._verify_password(form_data.password, user_orm.hashed_password):
                raise exception

            return cls._get_user_token(user_orm, form_data.scopes)

    @classmethod
    async def refresh_access_token(
        cls, uow: UnitOfWorkBase, refresh_token: str
    ) -> TokenSchema:
        exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                refresh_token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
            )
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            raise exception

        user_email = payload.get("sub")

        async with uow:
            user_orm = await uow.users.get_by_email(user_email)
            if not user_orm:
                raise exception

            return cls._get_user_token(user_orm, scopes=[])
