from fastapi import FastAPI, Request, Query, Depends, HTTPException
from fastapi.responses import RedirectResponse
from src.strava_interface import subscribe_to_strava
import uvicorn
from helpers import generate_random_string
from urllib.parse import urlencode
import os
import base64
from requests import post
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.db import get_db, User, Token
from src.auth import create_access_token, get_current_user
from datetime import datetime
from strava_models import StravaAuthResponse
from src.spotify import build_spotify_login_url, exchange_code_for_access_token

load_dotenv()

app = FastAPI()

BASE_URL = os.getenv("BASE_URL")
FRONTEND_URL = os.getenv("FRONTEND_URL")

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = f"{BASE_URL}/strava/callback"

STRAVA_SUB_CALLBACK_URL = os.getenv("STRAVA_CALLBACK_URL")
STRAVA_SUB_VERIFICATION_TOKEN = generate_random_string(16)


# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to Rebeat"}


# Protected endpoint to test authentication
@app.get("/api/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Returns the current authenticated user
    """
    return {
        "id": current_user.id,
        "strava_id": current_user.strava_id,
        "spotify_id": current_user.spotify_id,
        "created_at": current_user.created_at,
    }


# Begins the authorization process. Redirects to spotify's authorization page for user consent.
# More info at: https://developer.spotify.com/documentation/web-api/tutorials/code-flow
@app.get("/spotify/login")
def spotify_login():
    return RedirectResponse(build_spotify_login_url())


# Receives the code and state from spotify, and then exchanges the code for an access token
@app.get("/spotify/callback")
async def spotify_callback(request: Request):
    # TODO: Store state and compare to the state here.
    code: str | None = request.query_params.get("code")
    state: str | None = request.query_params.get("state")
    error: str | None = request.query_params.get("error")

    # If there is an error, redirect to the frontend with the error.
    if error:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=" + error)

    # If there is no state, redirect to the frontend with an error.
    if not state:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=no_state")

    # If there is no code, redirect to the frontend with an error.
    if not code:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=no_code")

    token_response = exchange_code_for_access_token(code)
    print(token_response)

    # TODO: Store the access token in the database associated with a user.
    # For now, just redirect to the frontend with the access token. (bad)
    return RedirectResponse(
        url=FRONTEND_URL + "?access_token=" + token_response["access_token"]
    )


@app.get("/strava/login")
def strava_login():
    """
    Redirects the user to Strava's OAuth authorization page.
    """
    STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
    STRAVA_SCOPE = "activity:read"

    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": STRAVA_REDIRECT_URI,
        "approval_prompt": "auto",
        "scope": STRAVA_SCOPE,
    }

    return RedirectResponse(f"{STRAVA_AUTH_URL}?{urlencode(params)}")


# A Strava auth flow redirects us back here with a code in the URL
# We can exchange the code for an access token and do what we will with it.
@app.get("/strava/callback")
def strava_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles Strava OAuth callback and creates user if not exists
    """
    code = request.query_params.get("code")
    if not code:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=no_code")

    # Exchange code for token
    access_token_url = "https://www.strava.com/oauth/token"
    params = {
        "client_id": STRAVA_CLIENT_ID,
        "client_secret": STRAVA_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
    }

    token_response = post(access_token_url, data=params).json()
    strava_auth = StravaAuthResponse.model_validate(token_response)

    # Extract Strava user ID from token response
    strava_id = str(strava_auth.athlete.id)
    access_token = strava_auth.access_token
    refresh_token = strava_auth.refresh_token
    expires_at = datetime.fromtimestamp(strava_auth.expires_at)

    # Check if user exists
    user = db.query(User).filter(User.strava_id == strava_id).first()
    if not user:
        # Create new user
        user = User(strava_id=strava_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Store/update token
    token = (
        db.query(Token)
        .filter(Token.user_id == user.id, Token.provider == "strava")
        .first()
    )

    if token:
        # Update existing token
        token.access_token = access_token
        token.refresh_token = refresh_token
        token.expires_at = expires_at
    else:
        # Create new token
        token = Token(
            user_id=user.id,
            provider="strava",
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        db.add(token)

    db.commit()

    # Generate JWT
    jwt_token = create_access_token(user.id)

    # Redirect to frontend with JWT
    return RedirectResponse(url=f"{FRONTEND_URL}?token={jwt_token}")


# NOT WORKING, INCOMPLETE: Strava GET request to verify the callback URL.
@app.get("/strava/webhook")
def verify_webhook(request: Request):

    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")

    print(hub_mode, hub_challenge, hub_verify_token)

    """
    Strava will send a GET request to verify the callback URL.
    Check if tokens match and respond back with hub.challenge.
    
    Args:
        hub_mode: str - Strava hub.mode.
        hub_challenge: str - Strava hub.challenge.
        hub_verify_token: str - Strava hub.verify_token.

    Returns:
        dict: hub.challenge if tokens match, error message otherwise.
    """
    if hub_mode != "subscribe":
        return {"error": "Invalid hub.mode"}

    if hub_verify_token == STRAVA_SUB_VERIFICATION_TOKEN:
        return {"hub.challenge": hub_challenge}

    return {"error": "Invalid verification token"}


# NOT WORKING, INCOMPLETE: Connect to Strava endpoint, kick things off with subscribe_to_strava.
@app.get("/strava/subscribe")
def connect_to_strava():
    """
    Trigger the Strava subscription process when a user visits this endpoint.
    """

    subscribe_to_strava(
        STRAVA_CLIENT_ID=STRAVA_CLIENT_ID,
        STRAVA_CLIENT_SECRET=STRAVA_CLIENT_SECRET,
        CALLBACK_URL=STRAVA_SUB_CALLBACK_URL,
        VERIFICATION_TOKEN=STRAVA_SUB_VERIFICATION_TOKEN,
    )

    return {"message": "Subscription request sent to Strava"}


# Run the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
