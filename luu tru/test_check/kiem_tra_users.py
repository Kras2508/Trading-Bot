"""
Kiem tra users trong database
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("KIEM TRA USERS TRONG DATABASE")
print("="*60)
print()

try:
    from app.database import SessionLocal
    from app.models.user import User
    
    db = SessionLocal()
    users = db.query(User).all()
    
    if not users:
        print("[INFO] Khong co user nao trong database")
        print("\nBan can tao user moi:")
        print("1. Dung API: POST /api/auth/register")
        print("2. Hoac dung frontend: Click 'Dang ky'")
    else:
        print(f"Tim thay {len(users)} user(s):\n")
        for i, user in enumerate(users, 1):
            print(f"User {i}:")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Active: {user.is_active}")
            print(f"  Admin: {user.is_admin}")
            print()
    
    db.close()
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

print("="*60)
print("\nTHONG TIN DANG NHAP:")
print("="*60)
print("Neu co user, su dung:")
print("  Username: (username tu database)")
print("  Password: (password ban da tao)")
print("\nNeu chua co user, tao moi qua frontend hoac API")
print("="*60)

