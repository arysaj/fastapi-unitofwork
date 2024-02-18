from typing import Annotated
from fastapi import APIRouter, Depends, status, Header
from fastapi.security import OAuth2PasswordRequestForm

from src.fastapi_unitofwork.schemas.token import TokenSchema
from src.fastapi_unitofwork.services.auth import AuthService
from src.fastapi_unitofwork.services.uow import UnitOfWorkBase, UnitOfWork

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/token", response_model=TokenSchema, status_code=status.HTTP_200_OK)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: Annotated[UnitOfWorkBase, Depends(UnitOfWork)],
    auth_service: Annotated[AuthService, Depends()],
) -> TokenSchema:
    return await auth_service.login_for_access_token(uow, form_data)


@auth_router.post(
    "/refresh-token", response_model=TokenSchema, status_code=status.HTTP_200_OK
)
async def refresh_access_token(
    uow: Annotated[UnitOfWorkBase, Depends(UnitOfWork)],
    auth_service: Annotated[AuthService, Depends()],
    refresh_token: Annotated[str, Header()],
) -> TokenSchema:
    return await auth_service.refresh_access_token(uow, refresh_token)
