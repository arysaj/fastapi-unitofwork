from typing import Annotated

import jwt
from fastapi import HTTPException, Depends, Security
from fastapi.security import SecurityScopes
from sqlalchemy.exc import IntegrityError
from starlette import status
from pydantic import ValidationError

from src.fastapi_unitofwork.models.user import UserModel
from src.fastapi_unitofwork.schemas.user import CreateUserRequest, UserResponse
from src.fastapi_unitofwork.schemas.token import TokenData
from src.fastapi_unitofwork.services.uow import UnitOfWorkBase, UnitOfWork
from src.fastapi_unitofwork.services.auth import pwd_context, oauth2_scheme
from src.fastapi_unitofwork.configs.settings import get_settings

settings = get_settings()


class UserService:
    @classmethod
    def _get_password_hash(cls, password: str) -> str:
        return pwd_context.hash(password)

    @classmethod
    async def create_user_account(
        cls, uow: UnitOfWorkBase, user_data: CreateUserRequest
    ) -> UserResponse:
        user_dict = user_data.dict()
        user_dict.update(
            {"hashed_password": cls._get_password_hash(user_data.password)}
        )
        user_dict.pop("password")
        new_user = UserModel(**user_dict)
        async with uow:
            try:
                user_orm = await uow.users.add(new_user)
                await uow.commit()
            except IntegrityError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"User {user_data.email} is already registered with us.",
                )

            return UserResponse.model_validate(user_orm)

    @staticmethod
    async def _get_current_user(
        security_scopes: SecurityScopes,
        token: Annotated[str, Depends(oauth2_scheme)],
        uow: Annotated[UnitOfWorkBase, Depends(UnitOfWork)],
    ) -> UserResponse:
        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
        else:
            authenticate_value = "Bearer"

        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        )
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=settings.ALGORITHM
            )
            user_email: str = payload.get("sub")
            if user_email is None:
                raise credentials_exception
            token_scope = payload.get("scopes", [])
            token_data = TokenData(user_email=user_email, scopes=token_scope)
        except (jwt.ExpiredSignatureError, ValidationError, jwt.DecodeError):
            raise credentials_exception

        async with uow:
            user_orm = await uow.users.get_by_email(token_data.user_email)

            if user_orm is None:
                raise credentials_exception

            for scope in security_scopes.scopes:
                if scope not in token_data.scopes:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Not enough permissions",
                        headers={"WWW-Authenticate": authenticate_value},
                    )

            return UserResponse.model_validate(user_orm)

    @staticmethod
    async def get_current_active_user(
        current_user: Annotated[
            UserResponse, Security(_get_current_user, scopes=["me"])
        ]
    ) -> UserModel:
        user = await current_user
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )

        return user
