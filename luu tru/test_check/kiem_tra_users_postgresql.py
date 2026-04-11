"""
Kiem tra users trong PostgreSQL database
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

print("="*60)
print("KIEM TRA USERS TRONG DATABASE")
print("="*60)
print()

try:
    from app.database import SessionLocal
    from app.models.user import User
    
    db = SessionLocal()
    
    # Get all users
    users = db.query(User).all()
    
    if not users:
        print("[INFO] Chua co user nao trong database!")
        print("\nBan can tao user de dang nhap:")
        print("1. Chay script: python tao_user_trong_db.py")
        print("2. Hoac dang ky qua API: POST /api/auth/register")
        print("3. Hoac qua Swagger UI: http://localhost:8000/docs")
    else:
        print(f"[OK] Tim thay {len(users)} user(s):\n")
        for user in users:
            print(f"  ID: {user.id}")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Admin: {'Yes' if user.is_admin else 'No'}")
            print(f"  Active: {'Yes' if user.is_active else 'No'}")
            print(f"  Created: {user.created_at}")
            print("-" * 40)
        
        print("\n" + "="*60)
        print("THONG TIN DANG NHAP:")
        print("="*60)
        print("Ban co the dang nhap voi bat ky user nao o tren")
        print("Neu khong nho password, chay script: python tao_user_trong_db.py")
        print("de reset password ve 'admin123'")
        print("="*60)
    
    db.close()
    
except Exception as e:
    print(f"[ERROR] Loi: {e}")
    import traceback
    traceback.print_exc()

