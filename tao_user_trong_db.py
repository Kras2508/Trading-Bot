"""
Tao user truc tiep trong database
"""
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("TAO USER TRONG DATABASE")
print("="*60)
print()

# Thong tin user
username = "admin"
email = "admin@example.com"
password = "admin123"

print(f"Username: {username}")
print(f"Email: {email}")
print(f"Password: {password}")
print()

try:
    from app.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    
    # Check if user exists
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"[WARN] User '{username}' da ton tai")
        print("Dang cap nhat password...")
        existing.hashed_password = get_password_hash(password)
        db.commit()
        print("[OK] Da cap nhat password!")
    else:
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=False
        )
        db.add(new_user)
        db.commit()
        print(f"[OK] Da tao user '{username}' thanh cong!")
    
    db.close()
    
    print("\n" + "="*60)
    print("THONG TIN DANG NHAP:")
    print("="*60)
    print(f"Username: {username}")
    print(f"Password: {password}")
    print("\nBan co the dang nhap vao frontend:")
    print("http://localhost:3000")
    print("="*60)
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

