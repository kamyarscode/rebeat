import logging
import os
from urllib.parse import urlencode
from src.strava_models import StravaAuthResponse
from src.helpers import build_state
from dotenv import load_dotenv
from requests import post, get
from sqlalchemy.orm import Session
from src.db import Token

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_SCOPE = "activity:read_all,activity:write"

STRAVA_REDIRECT_URI = f"{BASE_URL}/strava/callback"
STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
STRAVA_ACCESS_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_URL = "https://www.strava.com/api/v3"


def build_strava_auth_url(token: str):
    # Generate a state parameter to include the JWT token
    state = build_state(token=token)

    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": STRAVA_REDIRECT_URI,
        "approval_prompt": "auto",
        "scope": STRAVA_SCOPE,
        "state": state,
    }
    return f"{STRAVA_AUTH_URL}?{urlencode(params)}"


def exchange_strava_code_for_access_token(code: str):
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }
    response = post(STRAVA_ACCESS_TOKEN_URL, data=params).json()
    return StravaAuthResponse.model_validate(response)


def get_strava_access_token_from_db(user_id: int, db: Session):
    user = (
        db.query(Token)
        .filter(Token.user_id == user_id, Token.provider == "strava")
        .first()
    )
    # TODO: Refresh if expired
    return user.access_token


def get_latest_run(user_id: int, db: Session):
    access_token = get_strava_access_token_from_db(user_id, db)
    query_params = {
        "per_page": 1,
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    response = get(
        f"{STRAVA_API_URL}/athlete/activities",
        params=query_params,
        headers=headers,
    ).json()
    return {
        "id": response[0]["id"],
        "name": response[0]["name"],
        "distance": response[0]["distance"],
        "moving_time": response[0]["moving_time"],
        "start_date": response[0]["start_date"],
    }
