"""Test register directly"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.core.security import get_password_hash

# Ensure tables exist
Base.metadata.create_all(bind=engine)

# Test creating user
db = SessionLocal()
try:
    user = User(
        username="testuser_direct",
        email="testdirect@example.com",
        hashed_password=get_password_hash("test123"),
        is_admin=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"✅ User created successfully: {user.id} - {user.username}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

