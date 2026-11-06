from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt

from semantix.core.config import get_settings

ALGORITHM = "HS256"


def create_access_token(subject: str, *, expires_minutes: int | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(
        minutes=expires_minutes or settings.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("invalid_token") from exc
    subject = payload.get("sub")
    if not subject or not isinstance(subject, str):
        raise ValueError("invalid_token")
    return subject
