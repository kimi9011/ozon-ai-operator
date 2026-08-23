from __future__ import annotations
from datetime import datetime
from sqlalchemy import create_engine, String, Integer, Float, Boolean, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import database_url

class Base(DeclarativeBase): pass

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    offer_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    name: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(120), index=True)
    subcategory: Mapped[str | None] = mapped_column(String(120), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    listed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    sku_count: Mapped[int] = mapped_column(Integer, default=1)
    requires_certification: Mapped[bool] = mapped_column(Boolean, default=False)
    restricted_category: Mapped[bool] = mapped_column(Boolean, default=False)
    dangerous_goods: Mapped[bool] = mapped_column(Boolean, default=False)
    brand_risk_high: Mapped[bool] = mapped_column(Boolean, default=False)
    fragile: Mapped[bool] = mapped_column(Boolean, default=False)
    battery: Mapped[bool] = mapped_column(Boolean, default=False)
    return_risk_high: Mapped[bool] = mapped_column(Boolean, default=False)
    compatibility_complex: Mapped[bool] = mapped_column(Boolean, default=False)

class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"
    __table_args__ = (UniqueConstraint("date", "product_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    product_id: Mapped[str] = mapped_column(String(80), index=True)
    sales: Mapped[float] = mapped_column(Float, default=0)
    search_volume: Mapped[float] = mapped_column(Float, default=0)
    cart_additions: Mapped[float] = mapped_column(Float, default=0)
    seller_count: Mapped[float] = mapped_column(Float, default=0)
    lowest_price: Mapped[float] = mapped_column(Float, default=0)
    median_price: Mapped[float] = mapped_column(Float, default=0)

class StoreMetric(Base):
    __tablename__ = "store_daily_metrics"
    __table_args__ = (UniqueConstraint("date", "offer_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, index=True)
    offer_id: Mapped[str] = mapped_column(String(120), index=True)
    impressions: Mapped[float] = mapped_column(Float, default=0)
    clicks: Mapped[float] = mapped_column(Float, default=0)
    cart_additions: Mapped[float] = mapped_column(Float, default=0)
    orders: Mapped[float] = mapped_column(Float, default=0)
    revenue: Mapped[float] = mapped_column(Float, default=0)
    returns: Mapped[float] = mapped_column(Float, default=0)
    price: Mapped[float] = mapped_column(Float, default=0)
    stock: Mapped[float] = mapped_column(Float, default=0)

class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[str] = mapped_column(String(80), index=True)
    discovered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    source: Mapped[str] = mapped_column(String(80), default="manual")
    bucket: Mapped[str] = mapped_column(String(40), default="growth_30_90")
    score: Mapped[float] = mapped_column(Float, default=0)
    grade: Mapped[str] = mapped_column(String(20), default="NEW")
    status: Mapped[str] = mapped_column(String(30), default="NEW")
    reasons: Mapped[str | None] = mapped_column(Text, nullable=True)

class Lifecycle(Base):
    __tablename__ = "product_lifecycle"
    id: Mapped[int] = mapped_column(primary_key=True)
    offer_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="TESTING")
    last_decision_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

class StrategyHistory(Base):
    __tablename__ = "strategy_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    payload: Mapped[str] = mapped_column(Text)

engine = create_engine(database_url(), future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(engine)
