"""Seed demo users for local development."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.repositories import user_repo
from app.models.user import UserRole

DEMO_USERS = [
    {"email": "applicant@demo.com", "password": "Demo1234!", "full_name": "Demo Applicant", "role": UserRole.applicant},
    {"email": "bank@demo.com", "password": "Demo1234!", "full_name": "Bank Officer", "role": UserRole.bank_officer},
    {"email": "admin@demo.com", "password": "Demo1234!", "full_name": "System Admin", "role": UserRole.admin},
]

def seed():
    db = SessionLocal()
    try:
        for u in DEMO_USERS:
            existing = user_repo.get_by_email(db, u["email"])
            if existing:
                print(f"  Skipping {u['email']} (already exists)")
                continue
            from app.core.security import hash_password
            user_repo.create_user(
                db,
                email=u["email"],
                password_hash=hash_password(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
            )
            print(f"  Created {u['email']} ({u['role']})")
        print("Seeding complete.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
