from fastapi import APIRouter, status
from sqlalchemy import select

from apps.api.deps import CurrentUser, SessionDep
from apps.api.schemas import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from semantix.core.errors import AppError
from semantix.models.user import User
from semantix.security.auth import create_access_token
from semantix.security.password import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(body: RegisterRequest, session: SessionDep) -> User:
    existing = await session.scalar(select(User).where(User.email == body.email.lower()))
    if existing is not None:
        raise AppError("email_taken", "Email already registered", status_code=409)
    user = User(
        email=body.email.lower(),
        password_hash=hash_password(body.password),
        display_name=body.display_name,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: SessionDep) -> TokenResponse:
    user = await session.scalar(select(User).where(User.email == body.email.lower()))
    if user is None or not verify_password(body.password, user.password_hash):
        raise AppError("invalid_credentials", "Invalid email or password", status_code=401)
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> User:
    return user
