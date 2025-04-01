from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


# Basic config setup
# local set up:
DATABASE_URL = f"postgresql://{user}:{password}@localhost/genericdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define UserToken model and create table
# This model is used to store user tokens for Spotify and Strava.
class UserToken(Base):
    __tablename__ = "user_app_tokens"
    id = Column(Integer, primary_key=True, index=True)
    spotify_id = Column(String, unique=True, index=True)
    strava_id = Column(String, unique=True, index=True)
    app_name = Column(String, index=True)
    spotify_access_token = Column(String)
    spotify_refresh_token = Column(String)
    strava_access_token = Column(String)
    strava_access_token = Column(String)

# Create tables using base schema.
Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

