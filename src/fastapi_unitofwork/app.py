from fastapi import FastAPI

from fastapi_unitofwork.configs.settings import get_settings
from fastapi_unitofwork.metadata.tags import tags

from fastapi_unitofwork.routers.v1.auth import auth_router
from fastapi_unitofwork.routers.v1.users import user_router

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.API_VERSION, openapi_tags=tags)

app.include_router(auth_router)
app.include_router(user_router)
