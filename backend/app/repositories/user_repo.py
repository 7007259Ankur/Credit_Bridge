import hashlib
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import encrypt_field, decrypt_field


def _hash_email(email: str) -> str:
    return hashlib.sha256(email.lower().encode()).hexdigest()


def get_by_email(db: Session, email: str) -> Optional[User]:
    email_hash = _hash_email(email)
    return db.query(User).filter(User.email_hash == email_hash).first()


def get_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, email: str, password_hash: str, full_name: str, role) -> User:
    user = User(
        email_encrypted=encrypt_field(email),
        email_hash=_hash_email(email),
        password_hash=password_hash,
        full_name_encrypted=encrypt_field(full_name),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_email(user: User) -> str:
    return decrypt_field(user.email_encrypted)
