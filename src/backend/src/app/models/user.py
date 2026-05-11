from sqlalchemy import (
    BigInteger,
    Column,
    String,
    Integer,
    Boolean,
    JSON,
    DateTime,
    Text,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from src.app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    openid = Column(String(128), unique=True, index=True, nullable=True)
    unionid = Column(String(128), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    phone = Column(String(32), nullable=True)
    password_hash = Column(String(255), nullable=True)
    display_name = Column(String(200), nullable=False, default="")
    avatar_url = Column(Text, nullable=True)
    role = Column(String(32), nullable=False, default="user")
    balance_cents = Column(BigInteger, nullable=False, default=0)
    metadata_json = Column(JSON, nullable=True, name="metadata")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    addresses = relationship("Address", back_populates="user")
    files = relationship("File", back_populates="user")
    orders = relationship("Order", back_populates="user")

class Address(Base):
    __tablename__ = "addresses"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=True)
    recipient_name = Column(String(100), nullable=True)
    phone = Column(String(32), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    province = Column(String(100), nullable=True)
    postal_code = Column(String(32), nullable=True)
    country = Column(String(64), nullable=False, default="CN")
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="addresses")


class File(Base):
    __tablename__ = "files"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    filename = Column(String(512), nullable=True)
    storage_key = Column(String(1024), nullable=False)
    storage_provider = Column(String(32), nullable=False, default="s3")
    content_type = Column(String(128), nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    page_count = Column(Integer, nullable=True)
    checksum = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="uploaded")
    preview_url = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True, name="metadata")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="files")
    library_resources = relationship("LibraryResource", back_populates="file")

class Upload(Base):
    __tablename__ = "uploads"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    upload_id = Column(String(64), unique=True, nullable=False)
    storage_key = Column(String(1024), nullable=True)
    expected_size = Column(BigInteger, nullable=True)
    expected_content_type = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    fields_json = Column(JSON, nullable=True, name="fields")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    @property
    def fields(self):
        return self.fields_json

    @fields.setter
    def fields(self, value):
        self.fields_json = value


class Order(Base):
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    out_trade_no = Column(String(64), unique=True, nullable=True)
    total_cents = Column(BigInteger, nullable=False)
    currency = Column(String(8), nullable=False, default="CNY")
    status = Column(String(32), nullable=False, default="CREATED")
    payment_provider = Column(String(32), nullable=True)
    provider_payment_id = Column(String(128), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    address_id = Column(BigInteger, ForeignKey("addresses.id"), nullable=True)
    metadata_json = Column(JSON, nullable=True, name="metadata")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")
    address = relationship("Address")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=False)
    file_id = Column(BigInteger, ForeignKey("files.id"), nullable=True)
    description = Column(String(512), nullable=True)
    unit_price_cents = Column(BigInteger, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    options_json = Column(JSON, nullable=True, name="options")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    order = relationship("Order", back_populates="items")
    file = relationship("File")

    @property
    def options(self):
        return self.options_json

    @options.setter
    def options(self, value):
        self.options_json = value


class Payment(Base):
    __tablename__ = "payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=True)
    provider = Column(String(32), nullable=True)
    provider_payload = Column(JSON, nullable=True)
    provider_status = Column(String(32), nullable=True)
    amount_cents = Column(BigInteger, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    order = relationship("Order", back_populates="payments")


class PriceTable(Base):
    __tablename__ = "price_tables"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    version = Column(Integer, nullable=False)
    name = Column(String(255), nullable=True)
    published = Column(Boolean, nullable=False, default=False)
    rules = Column(JSON, nullable=False)
    created_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    published_at = Column(DateTime(timezone=True), nullable=True)


class LibraryCategory(Base):
    __tablename__ = "library_categories"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    resources = relationship("LibraryResource", back_populates="category")


class LibraryResource(Base):
    __tablename__ = "library_resources"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    category_id = Column(BigInteger, ForeignKey("library_categories.id"), nullable=True)
    title = Column(String(512), nullable=False)
    file_id = Column(BigInteger, ForeignKey("files.id"), nullable=True)
    page_count = Column(Integer, nullable=True)
    price_override_cents = Column(BigInteger, nullable=True)
    is_public = Column(Boolean, nullable=False, default=True)
    rights_info = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    category = relationship("LibraryCategory", back_populates="resources")
    file = relationship("File", back_populates="library_resources")


class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    admin_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=True)
    target_type = Column(String(64), nullable=True)
    target_id = Column(String(128), nullable=True)
    before_json = Column(JSON, nullable=True, name="before")
    after_json = Column(JSON, nullable=True, name="after")
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @property
    def before(self):
        return self.before_json

    @before.setter
    def before(self, value):
        self.before_json = value

    @property
    def after(self):
        return self.after_json

    @after.setter
    def after(self, value):
        self.after_json = value


class CustomerServiceSession(Base):
    __tablename__ = "customer_service_sessions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    order_id = Column(BigInteger, ForeignKey("orders.id"), nullable=True)
    session_provider = Column(String(64), nullable=True)
    provider_session_id = Column(String(128), nullable=True)
    metadata_json = Column(JSON, nullable=True, name="metadata")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
