# So Sánh SQL Server vs PostgreSQL - Insert/Update Data

## 1. INSERT DATA

### SQL Server
```sql
-- Basic INSERT
INSERT INTO users (username, email, password) 
VALUES ('admin', 'admin@example.com', 'hash123');

-- INSERT with IDENTITY (auto-increment)
INSERT INTO orders (symbol, side, amount) 
VALUES ('BTCUSDT', 'buy', 100.0);
-- ID tự động tăng

-- INSERT multiple rows
INSERT INTO users (username, email) 
VALUES 
    ('user1', 'user1@example.com'),
    ('user2', 'user2@example.com'),
    ('user3', 'user3@example.com');

-- INSERT with OUTPUT (return inserted values)
INSERT INTO orders (symbol, side, amount)
OUTPUT INSERTED.id, INSERTED.created_at
VALUES ('ETHUSDT', 'sell', 50.0);
```

### PostgreSQL
```sql
-- Basic INSERT (giống SQL Server)
INSERT INTO users (username, email, password) 
VALUES ('admin', 'admin@example.com', 'hash123');

-- INSERT with SERIAL/BIGSERIAL (auto-increment)
INSERT INTO orders (symbol, side, amount) 
VALUES ('BTCUSDT', 'buy', 100.0);
-- ID tự động tăng

-- INSERT multiple rows (giống SQL Server)
INSERT INTO users (username, email) 
VALUES 
    ('user1', 'user1@example.com'),
    ('user2', 'user2@example.com'),
    ('user3', 'user3@example.com');

-- INSERT with RETURNING (return inserted values)
INSERT INTO orders (symbol, side, amount)
VALUES ('ETHUSDT', 'sell', 50.0)
RETURNING id, created_at;
```

**Khác biệt:**
- SQL Server: `OUTPUT INSERTED.*`
- PostgreSQL: `RETURNING *`

---

## 2. UPDATE DATA

### SQL Server
```sql
-- Basic UPDATE
UPDATE users 
SET email = 'newemail@example.com' 
WHERE id = 1;

-- UPDATE with OUTPUT
UPDATE orders 
SET status = 'closed'
OUTPUT INSERTED.id, INSERTED.status, DELETED.status
WHERE id = 100;

-- UPDATE multiple columns
UPDATE bot_configs 
SET amount = 200.0, 
    stop_loss_percent = 3.0,
    updated_at = GETDATE()
WHERE id = 1;

-- UPDATE with JOIN
UPDATE o
SET o.status = 'filled'
FROM orders o
INNER JOIN bot_configs b ON o.bot_config_id = b.id
WHERE b.name = 'BTC Bot';
```

### PostgreSQL
```sql
-- Basic UPDATE (giống SQL Server)
UPDATE users 
SET email = 'newemail@example.com' 
WHERE id = 1;

-- UPDATE with RETURNING
UPDATE orders 
SET status = 'closed'
WHERE id = 100
RETURNING id, status;

-- UPDATE multiple columns (giống SQL Server)
UPDATE bot_configs 
SET amount = 200.0, 
    stop_loss_percent = 3.0,
    updated_at = NOW()
WHERE id = 1;

-- UPDATE with JOIN (syntax khác)
UPDATE orders o
SET status = 'filled'
FROM bot_configs b
WHERE o.bot_config_id = b.id 
  AND b.name = 'BTC Bot';
```

**Khác biệt:**
- SQL Server: `OUTPUT INSERTED.*` / `OUTPUT DELETED.*`
- PostgreSQL: `RETURNING *`
- SQL Server: `GETDATE()`
- PostgreSQL: `NOW()` hoặc `CURRENT_TIMESTAMP`
- UPDATE với JOIN: syntax hơi khác

---

## 3. DELETE DATA

### SQL Server
```sql
-- Basic DELETE
DELETE FROM users WHERE id = 1;

-- DELETE with OUTPUT
DELETE FROM orders
OUTPUT DELETED.id, DELETED.symbol
WHERE status = 'cancelled';

-- DELETE with JOIN
DELETE o
FROM orders o
INNER JOIN bot_configs b ON o.bot_config_id = b.id
WHERE b.is_active = false;
```

### PostgreSQL
```sql
-- Basic DELETE (giống SQL Server)
DELETE FROM users WHERE id = 1;

-- DELETE with RETURNING
DELETE FROM orders
WHERE status = 'cancelled'
RETURNING id, symbol;

-- DELETE with JOIN (syntax khác)
DELETE FROM orders o
USING bot_configs b
WHERE o.bot_config_id = b.id 
  AND b.is_active = false;
```

**Khác biệt:**
- SQL Server: `OUTPUT DELETED.*`
- PostgreSQL: `RETURNING *`
- DELETE với JOIN: SQL Server dùng `FROM ... INNER JOIN`, PostgreSQL dùng `USING`

---

## 4. UPSERT (INSERT or UPDATE)

### SQL Server
```sql
-- MERGE statement (SQL Server 2008+)
MERGE INTO users AS target
USING (VALUES ('admin', 'admin@example.com', 'hash123')) AS source (username, email, password)
ON target.username = source.username
WHEN MATCHED THEN
    UPDATE SET email = source.email, password = source.password
WHEN NOT MATCHED THEN
    INSERT (username, email, password) VALUES (source.username, source.email, source.password);
```

### PostgreSQL
```sql
-- INSERT ... ON CONFLICT (PostgreSQL 9.5+)
INSERT INTO users (username, email, password)
VALUES ('admin', 'admin@example.com', 'hash123')
ON CONFLICT (username) 
DO UPDATE SET 
    email = EXCLUDED.email,
    password = EXCLUDED.password;
```

**Khác biệt:**
- SQL Server: `MERGE` statement (phức tạp hơn, mạnh hơn)
- PostgreSQL: `INSERT ... ON CONFLICT` (đơn giản hơn, chỉ cho unique constraints)

---

## 5. BULK INSERT

### SQL Server
```sql
-- BULK INSERT từ file
BULK INSERT orders
FROM 'C:\data\orders.csv'
WITH (
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    FIRSTROW = 2
);

-- INSERT từ SELECT
INSERT INTO orders_backup
SELECT * FROM orders WHERE created_at > '2024-01-01';
```

### PostgreSQL
```sql
-- COPY từ file
COPY orders FROM 'C:/data/orders.csv' 
WITH (FORMAT csv, HEADER true, DELIMITER ',');

-- INSERT từ SELECT (giống SQL Server)
INSERT INTO orders_backup
SELECT * FROM orders WHERE created_at > '2024-01-01';
```

**Khác biệt:**
- SQL Server: `BULK INSERT`
- PostgreSQL: `COPY` (nhanh hơn, nhưng cần quyền file system)

---

## 6. AUTO-INCREMENT / IDENTITY

### SQL Server
```sql
-- IDENTITY column
CREATE TABLE orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    symbol VARCHAR(50),
    ...
);

-- Lấy ID vừa insert
INSERT INTO orders (symbol) VALUES ('BTCUSDT');
SELECT SCOPE_IDENTITY();  -- hoặc @@IDENTITY
```

### PostgreSQL
```sql
-- SERIAL/BIGSERIAL
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,  -- hoặc BIGSERIAL
    symbol VARCHAR(50),
    ...
);

-- Lấy ID vừa insert
INSERT INTO orders (symbol) VALUES ('BTCUSDT') RETURNING id;
-- hoặc dùng CURRVAL
SELECT CURRVAL('orders_id_seq');
```

**Khác biệt:**
- SQL Server: `IDENTITY(1,1)`, `SCOPE_IDENTITY()`
- PostgreSQL: `SERIAL`, `RETURNING id` hoặc `CURRVAL()`

---

## 7. DATETIME FUNCTIONS

### SQL Server
```sql
-- Current date/time
SELECT GETDATE();           -- 2024-01-15 10:30:45.123
SELECT GETUTCDATE();        -- UTC time
SELECT SYSDATETIME();       -- Higher precision

-- Date functions
SELECT DATEADD(day, 7, GETDATE());
SELECT DATEDIFF(day, '2024-01-01', GETDATE());
SELECT YEAR(GETDATE()), MONTH(GETDATE()), DAY(GETDATE());
```

### PostgreSQL
```sql
-- Current date/time
SELECT NOW();               -- 2024-01-15 10:30:45.123456+00
SELECT CURRENT_TIMESTAMP;   -- Same as NOW()
SELECT CURRENT_DATE;        -- Date only
SELECT CURRENT_TIME;        -- Time only

-- Date functions
SELECT NOW() + INTERVAL '7 days';
SELECT EXTRACT(DAY FROM NOW());
SELECT DATE_PART('year', NOW());
```

**Khác biệt:**
- SQL Server: `GETDATE()`, `DATEADD()`, `DATEDIFF()`
- PostgreSQL: `NOW()`, `INTERVAL`, `EXTRACT()`, `DATE_PART()`

---

## 8. STRING FUNCTIONS

### SQL Server
```sql
-- String concatenation
SELECT 'Hello' + ' ' + 'World';

-- String functions
SELECT LEN('Hello');           -- Length
SELECT SUBSTRING('Hello', 1, 3); -- 'Hel'
SELECT UPPER('hello');         -- 'HELLO'
SELECT LOWER('HELLO');         -- 'hello'
SELECT REPLACE('Hello', 'l', 'L'); -- 'HeLLo'
```

### PostgreSQL
```sql
-- String concatenation
SELECT 'Hello' || ' ' || 'World';
SELECT CONCAT('Hello', ' ', 'World');

-- String functions
SELECT LENGTH('Hello');        -- Length
SELECT SUBSTRING('Hello', 1, 3); -- 'Hel'
SELECT UPPER('hello');         -- 'HELLO'
SELECT LOWER('HELLO');         -- 'hello'
SELECT REPLACE('Hello', 'l', 'L'); -- 'HeLLo'
```

**Khác biệt:**
- SQL Server: `+` để nối chuỗi, `LEN()`
- PostgreSQL: `||` hoặc `CONCAT()`, `LENGTH()`

---

## 9. TRANSACTION & LOCKING

### SQL Server
```sql
-- Transaction
BEGIN TRANSACTION;
INSERT INTO orders ...;
UPDATE bot_configs ...;
COMMIT;  -- hoặc ROLLBACK;

-- Lock hints
SELECT * FROM orders WITH (NOLOCK);  -- Read uncommitted
SELECT * FROM orders WITH (UPDLOCK); -- Update lock
```

### PostgreSQL
```sql
-- Transaction (giống SQL Server)
BEGIN;
INSERT INTO orders ...;
UPDATE bot_configs ...;
COMMIT;  -- hoặc ROLLBACK;

-- Isolation levels
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SELECT * FROM orders;
```

**Khác biệt:**
- SQL Server: `BEGIN TRANSACTION`, lock hints `WITH (NOLOCK)`
- PostgreSQL: `BEGIN`, isolation levels qua `SET TRANSACTION`

---

## 10. LIMIT / TOP

### SQL Server
```sql
-- TOP
SELECT TOP 10 * FROM orders ORDER BY created_at DESC;

-- OFFSET/FETCH (SQL Server 2012+)
SELECT * FROM orders 
ORDER BY created_at DESC
OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;
```

### PostgreSQL
```sql
-- LIMIT
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;

-- LIMIT with OFFSET
SELECT * FROM orders 
ORDER BY created_at DESC
LIMIT 10 OFFSET 0;
```

**Khác biệt:**
- SQL Server: `TOP n` hoặc `FETCH NEXT n ROWS ONLY`
- PostgreSQL: `LIMIT n`

---

## TÓM TẮT KHÁC BIỆT CHÍNH

| Tính năng | SQL Server | PostgreSQL |
|-----------|------------|------------|
| **Return inserted/updated** | `OUTPUT INSERTED.*` | `RETURNING *` |
| **Current datetime** | `GETDATE()` | `NOW()` |
| **Auto-increment** | `IDENTITY(1,1)` | `SERIAL` |
| **Get last ID** | `SCOPE_IDENTITY()` | `RETURNING id` |
| **Upsert** | `MERGE` | `INSERT ... ON CONFLICT` |
| **Bulk insert** | `BULK INSERT` | `COPY` |
| **String concat** | `+` | `\|\|` hoặc `CONCAT()` |
| **String length** | `LEN()` | `LENGTH()` |
| **Limit rows** | `TOP n` | `LIMIT n` |
| **Date add** | `DATEADD()` | `+ INTERVAL` |
| **Lock hints** | `WITH (NOLOCK)` | `SET TRANSACTION` |

---

## LƯU Ý KHI MIGRATE

1. **OUTPUT vs RETURNING**: Cần thay đổi code khi migrate
2. **GETDATE() vs NOW()**: Cần update stored procedures/functions
3. **IDENTITY vs SERIAL**: Tự động convert khi dùng SQLAlchemy
4. **MERGE vs ON CONFLICT**: Cần viết lại logic upsert
5. **String functions**: Một số function names khác nhau
6. **Transaction**: Syntax giống nhau, nhưng behavior có thể khác

---

## VÍ DỤ TRONG PYTHON (SQLAlchemy)

SQLAlchemy tự động xử lý hầu hết khác biệt:

```python
# Insert - giống nhau cho cả 2
db.execute(insert(User).values(username='admin', email='admin@example.com'))
db.commit()

# Update - giống nhau
db.execute(update(User).where(User.id == 1).values(email='new@example.com'))
db.commit()

# Get last ID - SQLAlchemy tự động xử lý
result = db.execute(insert(Order).values(symbol='BTCUSDT'))
order_id = result.inserted_primary_key[0]  # Works for both!

# Bulk insert - giống nhau
db.execute(insert(User), [
    {'username': 'user1', 'email': 'user1@example.com'},
    {'username': 'user2', 'email': 'user2@example.com'},
])
db.commit()
```

**Kết luận**: Nếu dùng SQLAlchemy ORM, hầu hết code không cần thay đổi khi migrate từ SQL Server sang PostgreSQL!

