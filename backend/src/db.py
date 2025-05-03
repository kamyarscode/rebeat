from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy_utils import database_exists, create_database
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Database connection setup


def get_engine(user, password, host, port, db):
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    if not database_exists(DATABASE_URL):
        create_database(DATABASE_URL)
    engine = create_engine(DATABASE_URL, pool_size=50, echo=False)
    return engine


def get_engine_from_env():
    return get_engine(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        db=os.getenv("DB_NAME"),
    )


# Create engine and session factory
engine = get_engine_from_env()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Define User model
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    strava_id = Column(String, unique=True, nullable=True, index=True)
    spotify_id = Column(String, unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.now())

    # Relationship
    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")

    # Add a check constraint to ensure at least one ID is provided
    __table_args__ = (
        CheckConstraint(
            "strava_id IS NOT NULL OR spotify_id IS NOT NULL", name="check_id_not_null"
        ),
    )


# Define Token model for OAuth tokens
class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String)  # "spotify" or "strava"
    access_token = Column(String)
    refresh_token = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # Relationship
    user = relationship("User", back_populates="tokens")


# Create tables
Base.metadata.create_all(bind=engine)
