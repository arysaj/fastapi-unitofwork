from pydantic import BaseModel


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_email: str | None = None
    scopes: list[str] = []
