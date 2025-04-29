import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from src.db import Token


def generate_random_string(length):
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def store_token(
    db: Session,
    user_id: int,
    provider: str,
    access_token: str,
    refresh_token: str = None,
    expires_at: datetime = None,
):
    """
    Store or update a token in the database

    Args:
        db: Database session
        user_id: ID of the user to associate the token with
        provider: Service provider name (e.g., 'spotify', 'strava')
        access_token: OAuth access token
        refresh_token: OAuth refresh token
        expires_at: Token expiration datetime

    Returns:
        The new or updated Token object
    """
    # Check if token already exists
    token = (
        db.query(Token)
        .filter(Token.user_id == user_id, Token.provider == provider)
        .first()
    )

    if token:
        # Update existing token
        token.access_token = access_token
        if refresh_token:
            token.refresh_token = refresh_token
        if expires_at:
            token.expires_at = expires_at
    else:
        # Create new token
        token = Token(
            user_id=user_id,
            provider=provider,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        db.add(token)

    db.commit()
    return token
