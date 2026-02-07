import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Load .env locally (Koyeb auto-loads env vars)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,   # reconnect if DB drops
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


# ===============================
# MODELS
# ===============================

class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    currency = Column(String)
    price = Column(Float)
    timestamp = Column(DateTime)


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    currency = Column(String)
    target_price = Column(Float)
    email = Column(String)
    triggered = Column(Integer, default=0)


# ===============================
# CREATE TABLES
# ===============================
Base.metadata.create_all(bind=engine)
