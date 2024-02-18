from typing import Annotated

from fastapi import APIRouter, Depends, status, Security

from src.fastapi_unitofwork.schemas.user import UserResponse, CreateUserRequest
from src.fastapi_unitofwork.services.users import UserService
from src.fastapi_unitofwork.services.uow import UnitOfWorkBase, UnitOfWork

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: CreateUserRequest,
    uow: Annotated[UnitOfWorkBase, Depends(UnitOfWork)],
    user_service: Annotated[UserService, Depends()],
) -> UserResponse:
    return await user_service.create_user_account(uow, data)


@user_router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def read_users_me(
    current_user: Annotated[UserResponse, Depends(UserService.get_current_active_user)],
) -> UserResponse:
    return current_user


@user_router.get("/me/items", status_code=status.HTTP_200_OK)
async def read_own_items(
    current_user: Annotated[
        UserResponse, Security(UserService.get_current_active_user, scopes=["items"])
    ],
) -> list:
    return [{"item_id": "Foo", "owner": current_user.email}]
