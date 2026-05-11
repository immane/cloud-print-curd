# Data Model / Entities

This file defines the primary entities (tables) for the application derived from docs/design/mini_program_spec.md and docs/design/manage_spec.md. It includes DDL-like column lists, constraints, and short SQLAlchemy model snippets for core tables.

Guidelines
- Use MySQL 8 as the database.
- All timestamps are stored in UTC (columns named created_at, updated_at with timezone awareness handled by app).
- Use integer primary keys (BIGINT) where growth is expected. Use UUIDs for external references where useful.

Core entities
-------------

users
- Purpose: store user accounts (mini‑program users and admin users).
- Columns:
  - id BIGINT PRIMARY KEY AUTO_INCREMENT
  - openid VARCHAR(128) NULL UNIQUE -- WeChat openid for mini program users
  - unionid VARCHAR(128) NULL UNIQUE
  - email VARCHAR(255) NULL UNIQUE
  - phone VARCHAR(32) NULL
  - password_hash VARCHAR(255) NULL -- nullable for mini‑program users logged-in via openid
  - display_name VARCHAR(200)
  - avatar_url TEXT
  - role VARCHAR(32) NOT NULL DEFAULT 'user' -- user, admin, operator, finance, support
  - balance_cents BIGINT NOT NULL DEFAULT 0
  - metadata JSON NULL
  - created_at DATETIME(6) NOT NULL
  - updated_at DATETIME(6) NOT NULL

indexes & notes:
- index on (openid), (email), (phone). Keep role small set.

addresses
- Purpose: user shipping / pickup addresses.
- Columns:
  - id BIGINT PK
  - user_id BIGINT FK -> users.id
  - title VARCHAR(100) -- (Home, Office)
  - recipient_name VARCHAR(100)
  - phone VARCHAR(32)
  - address_line1 VARCHAR(255)
  - address_line2 VARCHAR(255)
  - city VARCHAR(100)
  - province VARCHAR(100)
  - postal_code VARCHAR(32)
  - country VARCHAR(64) DEFAULT 'CN'
  - is_default BOOL DEFAULT FALSE
  - created_at, updated_at

files
- Purpose: uploaded files and library resource binaries
- Columns:
  - id BIGINT PK
  - user_id BIGINT FK -> users.id (nullable for public library resources)
  - filename VARCHAR(512)
  - storage_key VARCHAR(1024) NOT NULL -- key in S3 / Qiniu
  - storage_provider VARCHAR(32) NOT NULL DEFAULT 's3' -- s3, qiniu
  - content_type VARCHAR(128)
  - size_bytes BIGINT
  - page_count INT NULL
  - checksum VARCHAR(128) NULL
  - status VARCHAR(32) NOT NULL DEFAULT 'uploaded' -- uploaded / processing / ready / deleted
  - preview_url TEXT NULL
  - metadata JSON NULL
  - created_at, updated_at

uploads
- Purpose: transient upload intents (presigned tokens)
- Columns:
  - id BIGINT PK
  - user_id BIGINT FK
  - upload_id UUID / VARCHAR(64) UNIQUE
  - storage_key VARCHAR(1024)
  - expected_size BIGINT
  - expected_content_type VARCHAR(128)
  - status VARCHAR(32) DEFAULT 'pending' -- pending / uploaded / verified / failed
  - fields JSON NULL -- tokens/fields returned to client
  - created_at, updated_at

orders
- Purpose: print orders
- Columns:
  - id BIGINT PK
  - user_id BIGINT FK
  - out_trade_no VARCHAR(64) UNIQUE -- external order ref
  - total_cents BIGINT NOT NULL
  - currency VARCHAR(8) DEFAULT 'CNY'
  - status VARCHAR(32) NOT NULL DEFAULT 'created' -- see order statuses in spec
  - payment_provider VARCHAR(32) NULL
  - provider_payment_id VARCHAR(128) NULL
  - paid_at DATETIME(6) NULL
  - address_id BIGINT FK -> addresses.id NULL
  - metadata JSON NULL
  - created_at, updated_at

order_items
- Purpose: items inside orders (files + options)
- Columns:
  - id BIGINT PK
  - order_id BIGINT FK -> orders.id
  - file_id BIGINT FK -> files.id NULL -- resource or uploaded file
  - description VARCHAR(512)
  - unit_price_cents BIGINT
  - quantity INT
  - options JSON NULL -- paper_type, size, color, duplex etc.
  - created_at, updated_at

payments
- Purpose: raw payment records / webhooks
- Columns:
  - id BIGINT PK
  - order_id BIGINT FK
  - provider VARCHAR(32)
  - provider_payload JSON -- raw webhook payload
  - provider_status VARCHAR(32)
  - amount_cents BIGINT
  - created_at, updated_at

price_tables
- Purpose: versioned price tables
- Columns:
  - id BIGINT PK
  - version INT NOT NULL
  - name VARCHAR(255)
  - published BOOL DEFAULT FALSE
  - rules JSON NOT NULL -- structured rules grouped by paper_type and size
  - created_by BIGINT FK -> users.id
  - created_at, published_at

library_categories
- Purpose: tags/categories for public resources
- Columns:
  - id BIGINT PK
  - name VARCHAR(200)
  - slug VARCHAR(200) UNIQUE
  - order INT DEFAULT 0
  - created_at, updated_at

library_resources
- Purpose: public resources (books, templates)
- Columns:
  - id BIGINT PK
  - category_id BIGINT FK -> library_categories.id
  - title VARCHAR(512)
  - file_id BIGINT FK -> files.id
  - page_count INT
  - price_override_cents BIGINT NULL
  - is_public BOOL DEFAULT TRUE
  - rights_info JSON NULL
  - created_at, updated_at

admin_audit_logs
- Purpose: track admin actions for compliance
- Columns:
  - id BIGINT PK
  - admin_user_id BIGINT FK -> users.id
  - action VARCHAR(255)
  - target_type VARCHAR(64)
  - target_id VARCHAR(128)
  - before JSON NULL
  - after JSON NULL
  - ip_address VARCHAR(64) NULL
  - created_at DATETIME(6)

customer_service_sessions
- Purpose: map chat sessions to orders / users
- Columns:
  - id BIGINT PK
  - user_id BIGINT FK
  - order_id BIGINT FK NULL
  - session_provider VARCHAR(64) -- wechat / tencent_im / plugin
  - provider_session_id VARCHAR(128)
  - metadata JSON NULL
  - created_at, updated_at

notes on types & relations
- Use FK constraints with ON DELETE SET NULL for optional relations (e.g., file -> library_resource) and ON DELETE CASCADE for dependent entities where appropriate (e.g., order_items when order deleted).
- Consider adding read replicas for reporting queries and using partitioning or archival strategy for very large tables (payments, audit logs).

Example SQLAlchemy snippets (concise)
```python
from sqlalchemy import BigInteger, Column, String, Integer, JSON, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    openid = Column(String(128), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    display_name = Column(String(200))
    role = Column(String(32), nullable=False, default='user')
    balance_cents = Column(BigInteger, default=0)
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Order(Base):
    __tablename__ = 'orders'
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    out_trade_no = Column(String(64), unique=True, index=True)
    total_cents = Column(BigInteger, nullable=False)
    status = Column(String(32), nullable=False, default='created')
    payment_provider = Column(String(32))
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User')
```

This file is a starting point. When implementing, create Alembic migrations corresponding to these schemas and refine column sizes and JSON shapes based on concrete API payloads.
