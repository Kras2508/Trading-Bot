"""
Script migrate du lieu tu SQLite sang SQL Server
"""
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("MIGRATE DU LIEU TU SQLITE SANG SQL SERVER")
print("="*60)
print()

# SQLite connection
sqlite_url = "sqlite:///./trading_bot.db"
print(f"SQLite: {sqlite_url}")

# SQL Server connection (from .env)
from app.core.config import settings
sqlserver_url = settings.DATABASE_URL
print(f"SQL Server: {sqlserver_url}")
print()

# Confirm
confirm = input("Ban co muon migrate du lieu? (yes/no) [yes]: ").strip().lower() or "yes"
if confirm != "yes":
    print("Da huy.")
    sys.exit(0)

print("\nBuoc 1: Ket noi databases...")
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # SQLite engine
    sqlite_engine = create_engine(sqlite_url, echo=False)
    SQLiteSession = sessionmaker(bind=sqlite_engine)
    
    # SQL Server engine
    sqlserver_engine = create_engine(sqlserver_url, echo=False)
    SQLServerSession = sessionmaker(bind=sqlserver_engine)
    
    print("[OK] Ket noi thanh cong!")
    
except Exception as e:
    print(f"[ERROR] Loi ket noi: {e}")
    sys.exit(1)

print("\nBuoc 2: Migrate Users...")
try:
    from app.models.user import User
    
    sqlite_db = SQLiteSession()
    sqlserver_db = SQLServerSession()
    
    users = sqlite_db.query(User).all()
    print(f"Tim thay {len(users)} user(s)")
    
    migrated_users = 0
    for user in users:
        # Check if exists
        existing = sqlserver_db.query(User).filter(User.username == user.username).first()
        if existing:
            print(f"  [SKIP] User '{user.username}' da ton tai")
            continue
        
        # Create new user
        new_user = User(
            username=user.username,
            email=user.email,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        sqlserver_db.add(new_user)
        migrated_users += 1
        print(f"  [OK] Migrated user: {user.username}")
    
    sqlserver_db.commit()
    print(f"[OK] Da migrate {migrated_users} user(s)")
    
    sqlite_db.close()
    sqlserver_db.close()
    
except Exception as e:
    print(f"[ERROR] Loi migrate users: {e}")
    import traceback
    traceback.print_exc()

print("\nBuoc 3: Migrate Bot Configs...")
try:
    from app.models.bot_config import BotConfig
    
    sqlite_db = SQLiteSession()
    sqlserver_db = SQLServerSession()
    
    configs = sqlite_db.query(BotConfig).all()
    print(f"Tim thay {len(configs)} config(s)")
    
    # Get user mapping
    user_map = {}
    sqlite_users = sqlite_db.query(User).all()
    sqlserver_users = sqlserver_db.query(User).all()
    for su in sqlite_users:
        for ssu in sqlserver_users:
            if su.username == ssu.username:
                user_map[su.id] = ssu.id
                break
    
    migrated_configs = 0
    for config in configs:
        # Check if exists
        existing = sqlserver_db.query(BotConfig).filter(BotConfig.name == config.name).first()
        if existing:
            print(f"  [SKIP] Config '{config.name}' da ton tai")
            continue
        
        # Map created_by
        created_by = None
        if config.created_by and config.created_by in user_map:
            created_by = user_map[config.created_by]
        
        # Create new config
        new_config = BotConfig(
            name=config.name,
            symbol=config.symbol,
            exchange=config.exchange,
            amount=config.amount,
            leverage=config.leverage,
            stop_loss_percent=config.stop_loss_percent,
            take_profit_percent=config.take_profit_percent,
            tp_levels=config.tp_levels,
            enable_trailing=config.enable_trailing,
            trailing_type=config.trailing_type,
            trailing_percent=config.trailing_percent,
            trailing_atr_multiplier=config.trailing_atr_multiplier,
            trailing_atr_period=config.trailing_atr_period,
            api_key_encrypted=config.api_key_encrypted,  # Keep encrypted data
            api_secret_encrypted=config.api_secret_encrypted,  # Keep encrypted data
            trading_mode=config.trading_mode,
            max_open_positions=config.max_open_positions,
            enable_notifications=config.enable_notifications,
            is_active=config.is_active,
            created_by=created_by,
            created_at=config.created_at,
            updated_at=config.updated_at
        )
        sqlserver_db.add(new_config)
        migrated_configs += 1
        print(f"  [OK] Migrated config: {config.name} ({config.symbol})")
    
    sqlserver_db.commit()
    print(f"[OK] Da migrate {migrated_configs} config(s)")
    
    sqlite_db.close()
    sqlserver_db.close()
    
except Exception as e:
    print(f"[ERROR] Loi migrate configs: {e}")
    import traceback
    traceback.print_exc()

print("\nBuoc 4: Migrate Bot Status...")
try:
    from app.models.bot_status import BotStatus
    
    sqlite_db = SQLiteSession()
    sqlserver_db = SQLServerSession()
    
    statuses = sqlite_db.query(BotStatus).all()
    print(f"Tim thay {len(statuses)} status(es)")
    
    # Get config mapping
    config_map = {}
    sqlite_configs = sqlite_db.query(BotConfig).all()
    sqlserver_configs = sqlserver_db.query(BotConfig).all()
    for sc in sqlite_configs:
        for ssc in sqlserver_configs:
            if sc.name == ssc.name:
                config_map[sc.id] = ssc.id
                break
    
    migrated_statuses = 0
    for status in statuses:
        # Check if exists
        if status.bot_config_id in config_map:
            new_config_id = config_map[status.bot_config_id]
            existing = sqlserver_db.query(BotStatus).filter(BotStatus.bot_config_id == new_config_id).first()
            if existing:
                print(f"  [SKIP] Status cho config ID {new_config_id} da ton tai")
                continue
        else:
            print(f"  [SKIP] Khong tim thay config mapping cho bot_config_id {status.bot_config_id}")
            continue
        
        # Create new status
        new_status = BotStatus(
            bot_config_id=new_config_id,
            is_running=status.is_running,
            is_paused=status.is_paused,
            last_activity=status.last_activity,
            total_orders=status.total_orders,
            successful_orders=status.successful_orders,
            failed_orders=status.failed_orders,
            total_pnl=status.total_pnl,
            current_positions=status.current_positions,
            last_error=status.last_error,
            last_error_time=status.last_error_time,
            last_heartbeat=status.last_heartbeat,
            health_status=status.health_status,
            created_at=status.created_at,
            updated_at=status.updated_at
        )
        sqlserver_db.add(new_status)
        migrated_statuses += 1
        print(f"  [OK] Migrated status cho config ID {new_config_id}")
    
    sqlserver_db.commit()
    print(f"[OK] Da migrate {migrated_statuses} status(es)")
    
    sqlite_db.close()
    sqlserver_db.close()
    
except Exception as e:
    print(f"[ERROR] Loi migrate statuses: {e}")
    import traceback
    traceback.print_exc()

print("\nBuoc 5: Migrate Orders...")
try:
    from app.models.order import Order
    
    sqlite_db = SQLiteSession()
    sqlserver_db = SQLServerSession()
    
    orders = sqlite_db.query(Order).all()
    print(f"Tim thay {len(orders)} order(s)")
    
    # Get config mapping (reuse from previous step)
    if 'config_map' not in locals():
        config_map = {}
        sqlite_configs = sqlite_db.query(BotConfig).all()
        sqlserver_configs = sqlserver_db.query(BotConfig).all()
        for sc in sqlite_configs:
            for ssc in sqlserver_configs:
                if sc.name == ssc.name:
                    config_map[sc.id] = ssc.id
                    break
    
    migrated_orders = 0
    for order in orders:
        # Check if exists
        if order.exchange_order_id:
            existing = sqlserver_db.query(Order).filter(Order.exchange_order_id == order.exchange_order_id).first()
            if existing:
                print(f"  [SKIP] Order '{order.exchange_order_id}' da ton tai")
                continue
        
        # Map bot_config_id
        if order.bot_config_id not in config_map:
            print(f"  [SKIP] Khong tim thay config mapping cho bot_config_id {order.bot_config_id}")
            continue
        
        new_config_id = config_map[order.bot_config_id]
        
        # Create new order
        new_order = Order(
            bot_config_id=new_config_id,
            exchange_order_id=order.exchange_order_id,
            symbol=order.symbol,
            side=order.side,
            order_type=order.order_type,
            amount=order.amount,
            price=order.price,
            leverage=order.leverage,
            status=order.status,
            filled_amount=order.filled_amount,
            filled_price=order.filled_price,
            stop_loss_price=order.stop_loss_price,
            take_profit_price=order.take_profit_price,
            tp_levels=order.tp_levels,
            trailing_enabled=order.trailing_enabled,
            trailing_high_price=order.trailing_high_price,
            trailing_stop_price=order.trailing_stop_price,
            pnl=order.pnl,
            pnl_percent=order.pnl_percent,
            exchange=order.exchange,
            trading_mode=order.trading_mode,
            raw_data=order.raw_data,
            error_message=order.error_message,
            created_at=order.created_at,
            updated_at=order.updated_at,
            closed_at=order.closed_at
        )
        sqlserver_db.add(new_order)
        migrated_orders += 1
        print(f"  [OK] Migrated order: {order.id} - {order.symbol} - {order.side}")
    
    sqlserver_db.commit()
    print(f"[OK] Da migrate {migrated_orders} order(s)")
    
    sqlite_db.close()
    sqlserver_db.close()
    
except Exception as e:
    print(f"[ERROR] Loi migrate orders: {e}")
    import traceback
    traceback.print_exc()

print("\nBuoc 6: Migrate Activity Logs...")
try:
    from app.models.activity_log import ActivityLog
    
    sqlite_db = SQLiteSession()
    sqlserver_db = SQLServerSession()
    
    logs = sqlite_db.query(ActivityLog).all()
    print(f"Tim thay {len(logs)} log(s)")
    
    # Get config and order mappings
    if 'config_map' not in locals():
        config_map = {}
        sqlite_configs = sqlite_db.query(BotConfig).all()
        sqlserver_configs = sqlserver_db.query(BotConfig).all()
        for sc in sqlite_configs:
            for ssc in sqlserver_configs:
                if sc.name == ssc.name:
                    config_map[sc.id] = ssc.id
                    break
    
    # Get order mapping
    order_map = {}
    sqlite_orders = sqlite_db.query(Order).all()
    sqlserver_orders = sqlserver_db.query(Order).all()
    for so in sqlite_orders:
        for sso in sqlserver_orders:
            if so.exchange_order_id and sso.exchange_order_id and so.exchange_order_id == sso.exchange_order_id:
                order_map[so.id] = sso.id
                break
    
    migrated_logs = 0
    for log in logs:
        # Map bot_config_id
        new_config_id = None
        if log.bot_config_id and log.bot_config_id in config_map:
            new_config_id = config_map[log.bot_config_id]
        
        # Map order_id
        new_order_id = None
        if log.order_id and log.order_id in order_map:
            new_order_id = order_map[log.order_id]
        
        # Create new log
        new_log = ActivityLog(
            bot_config_id=new_config_id,
            order_id=new_order_id,
            level=log.level,
            category=log.category,
            message=log.message,
            details=log.details,
            source_ip=log.source_ip,
            user_agent=log.user_agent,
            created_at=log.created_at
        )
        sqlserver_db.add(new_log)
        migrated_logs += 1
    
    sqlserver_db.commit()
    print(f"[OK] Da migrate {migrated_logs} log(s)")
    
    sqlite_db.close()
    sqlserver_db.close()
    
except Exception as e:
    print(f"[ERROR] Loi migrate logs: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("HOAN TAT MIGRATE!")
print("="*60)
print("Da migrate du lieu tu SQLite sang SQL Server")
print("Vui long kiem tra du lieu trong SQL Server Management Studio")
print("="*60)

