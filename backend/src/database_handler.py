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


# Function to add user token to database
def add_user_token(db: Session, user_token: UserToken):
    db.add(user_token)
    db.commit()
    db.refresh(user_token)
    return user_token


# Define these tomorrow
def save_token(db: Session, user_id: str, app_name: str, access_token: str, refresh_token: str):
    token = UserToken(user_id=user_id, app_name=app_name, access_token=access_token, refresh_token=refresh_token)
    db.add(token)
    db.commit()

    db.refresh(token)
    return token

def get_token(db: Session, user_id: str, app_name: str):
    return db.query(UserToken).filter(UserToken.user_id == user_id, UserToken.app_name == app_name).first()

def update_token(db: Session, user_id: str, app_name: str, new_access_token: str):
    token = get_token(db, user_id, app_name)
    if token:
        token.access_token = new_access_token
        db.commit()

        db.refresh(token)
        return token
    
def delete_token(db: Session, user_id: str, app_name: str):
    token = get_token(db, user_id, app_name)
    if token:
        db.delete(token)
        db.commit()
        return True
    return False