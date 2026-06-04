from sqlalchemy.orm import Session
from jose import JWTError
from fastapi import HTTPException, status

from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)
from app.repositories import user_repo, audit_repo
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.models.user import UserRole


def register(db: Session, req: RegisterRequest) -> TokenResponse:
    existing = user_repo.get_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_repo.create_user(
        db,
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        role=req.role,
    )
    audit_repo.log(db, "user.registered", user_id=user.id, metadata={"role": req.role})
    return _issue_tokens(user)


def login(db: Session, req: LoginRequest) -> TokenResponse:
    user = user_repo.get_by_email(db, req.email)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    audit_repo.log(db, "user.login", user_id=user.id)
    return _issue_tokens(user)


def refresh(db: Session, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload["sub"])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = user_repo.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return _issue_tokens(user)


def _issue_tokens(user) -> TokenResponse:
    data = {"sub": str(user.id), "role": user.role}
    return TokenResponse(
        access_token=create_access_token(data),
        refresh_token=create_refresh_token(data),
    )
