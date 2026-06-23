from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from zoneinfo import ZoneInfo

BASE = declarative_base()
engine = create_engine("sqlite:///expenses.db")
Session = sessionmaker(bind=engine)

TIMEZONE = ZoneInfo("Asia/Yerevan")


def now():
    return datetime.now(TIMEZONE)


# ---------------- TABLE ----------------
class Expense(BASE):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True)
    user = Column(String)

    amount = Column(Float)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=now)


class Gas(BASE):
    __tablename__ = "gas"

    id = Column(Integer, primary_key=True)
    user = Column(String)
    amount = Column(Float)     # total fuel cost
    price = Column(Float)      # total price
    liters = Column(Float)
    km = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=now)


class Benzin(BASE):
    __tablename__ = "benzin"

    id = Column(Integer, primary_key=True)
    user = Column(String)
    amount = Column(Float)
    price = Column(Float)
    liters = Column(Float)
    created_at = Column(DateTime, default=now)


BASE.metadata.create_all(engine)
