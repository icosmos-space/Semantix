from typing import Annotated

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from semantix.core.db import get_session
from semantix.core.errors import AppError
from semantix.models.user import User
from semantix.security.auth import decode_access_token

bearer = HTTPBearer(auto_error=False)
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(
    session: SessionDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)] = None,
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    token: str | None = None
    if credentials is not None:
        token = credentials.credentials
    elif authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise AppError("unauthorized", "Authentication required", status_code=401)
    try:
        user_id = decode_access_token(token)
    except ValueError as exc:
        raise AppError("unauthorized", "Invalid or expired token", status_code=401) from exc
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise AppError("unauthorized", "User not found", status_code=401)
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
