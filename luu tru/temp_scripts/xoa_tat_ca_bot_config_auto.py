"""
Script để xóa tất cả bot configs (tự động xác nhận)
"""
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.bot_config import BotConfig
from app.models.order import Order
from app.models.bot_status import BotStatus

def xoa_tat_ca_bot_config(auto_confirm=False):
    """Xóa tất cả bot configs và các dữ liệu liên quan"""
    db: Session = SessionLocal()
    
    try:
        # Đếm số lượng configs
        total_configs = db.query(BotConfig).count()
        print(f"Tìm thấy {total_configs} bot config(s)")
        
        if total_configs == 0:
            print("Không có bot config nào để xóa.")
            return
        
        # Đếm số lượng orders liên quan
        all_config_ids = [config.id for config in db.query(BotConfig).all()]
        total_orders = db.query(Order).filter(Order.bot_config_id.in_(all_config_ids)).count()
        
        print(f"Tìm thấy {total_orders} order(s) liên quan")
        
        # Xác nhận
        print("\n" + "="*50)
        print("CẢNH BÁO: Bạn sắp xóa:")
        print(f"  - {total_configs} bot config(s)")
        print(f"  - {total_orders} order(s) liên quan")
        print(f"  - Tất cả bot status liên quan")
        print("="*50)
        
        if not auto_confirm:
            confirm = input("\nBạn có chắc chắn muốn xóa TẤT CẢ? (yes/no): ")
            if confirm.lower() != "yes":
                print("Đã hủy. Không có gì bị xóa.")
                return
        else:
            print("\n✅ Tự động xác nhận: YES - Bắt đầu xóa...")
        
        # Xóa orders trước
        if total_orders > 0:
            print(f"\nĐang xóa {total_orders} order(s)...")
            deleted_orders = db.query(Order).filter(Order.bot_config_id.in_(all_config_ids)).delete(synchronize_session=False)
            print(f"Đã xóa {deleted_orders} order(s)")
        else:
            deleted_orders = 0
        
        # Xóa bot status
        print(f"\nĐang xóa bot status...")
        deleted_status = db.query(BotStatus).filter(BotStatus.bot_config_id.in_(all_config_ids)).delete(synchronize_session=False)
        print(f"Đã xóa {deleted_status} bot status(es)")
        
        # Xóa bot configs
        print(f"\nĐang xóa {total_configs} bot config(s)...")
        deleted_configs = db.query(BotConfig).delete()
        print(f"Đã xóa {deleted_configs} bot config(s)")
        
        # Commit
        db.commit()
        
        print("\n" + "="*50)
        print("✅ HOÀN TẤT!")
        print(f"  - Đã xóa {deleted_configs} bot config(s)")
        print(f"  - Đã xóa {deleted_orders} order(s)")
        print(f"  - Đã xóa {deleted_status} bot status(es)")
        print("="*50)
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("="*50)
    print("SCRIPT XÓA TẤT CẢ BOT CONFIGS")
    print("="*50)
    print()
    
    # Tự động xác nhận nếu có tham số --yes
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv
    xoa_tat_ca_bot_config(auto_confirm=auto_confirm)

