import random
import string
from datetime import datetime
from sqlalchemy.orm import Session
from src.db import Token, User
from src.auth import verify_token


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


def find_or_create_user(
    db: Session, provider: str, provider_id: str, rebeat_jwt: str = None
):
    """
    Find or create a user based on a provider ID and JWT token

    Args:
        db: Database session
        provider: Service provider name (e.g., 'spotify', 'strava')
        provider_id: ID from the external provider
        rebeat_jwt: Optional JWT token that may contain existing user info

    Returns:
        User object
    """
    # Check provider field name based on provider type
    provider_field = f"{provider}_id"

    # Check if user exists with this provider ID
    filter_args = {provider_field: provider_id}
    user = db.query(User).filter_by(**filter_args).first()

    # If no user with this provider ID, try to get from JWT if provided
    if not user and rebeat_jwt:
        user_id = verify_token(rebeat_jwt)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()

            # Link provider account to existing user
            if user and not getattr(user, provider_field):
                setattr(user, provider_field, provider_id)
                db.commit()

    # If still no user, create new account
    if not user:
        # Create new user with provider ID
        new_user_args = {provider_field: provider_id}
        user = User(**new_user_args)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user
