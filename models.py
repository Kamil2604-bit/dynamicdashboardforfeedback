import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.orm import declarative_base, sessionmaker

# 1. READ FROM ENVIRONMENT VARIABLE (Keeps your password safe!)
# If it's missing, default to local SQLite.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gniot_dashboard.db")

# 2. Setup Engine
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Use this for PostgreSQL (Neon)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Feedback(Base):
    __tablename__ = "trainer_feedback"

    id = Column(Integer, primary_key=True, index=True)
    trainer_name = Column(String, index=True)
    date = Column(Date, index=True)
    subject = Column(String)
    rating = Column(Float)
    difficulties = Column(String, nullable=True)
    remarks = Column(String, nullable=True)

# Generate tables automatically
Base.metadata.create_all(bind=engine)