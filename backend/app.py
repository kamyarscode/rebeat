from fastapi import FastAPI, Request, Query, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from src.strava_interface import subscribe_to_strava
import uvicorn
from helpers import generate_random_string, store_token
from urllib.parse import urlencode
import os
import base64
from requests import post, get
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.db import get_db, User, Token
from src.auth import create_access_token, get_current_user
from datetime import datetime, timedelta
from strava_models import StravaAuthResponse
from src.spotify import (
    build_spotify_login_url,
    exchange_code_for_access_token,
    decode_state,
)

load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def spotify_login(request: Request):
    # Get JWT token if it's in the request
    jwt_token = request.query_params.get("token")

    # Pass the token to be encoded in the state parameter
    spotify_url = build_spotify_login_url(token=jwt_token)

    return RedirectResponse(spotify_url)


# Receives the code and state from spotify, and then exchanges the code for an access token
@app.get("/spotify/callback")
async def spotify_callback(request: Request, db: Session = Depends(get_db)):
    # Get parameters from the request
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

    # Decode the state to extract any token
    decoded_state = decode_state(state)
    jwt_token = decoded_state.get("token")

    # Exchange the code for tokens
    token_response = exchange_code_for_access_token(code)

    if "error" in token_response or "access_token" not in token_response:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=token_exchange_failed")

    # Get Spotify user profile to get user ID
    spotify_access_token = token_response["access_token"]
    refresh_token = token_response.get("refresh_token")
    expires_in = token_response.get(
        "expires_in", 3600
    )  # Default to 1 hour if not provided

    # Get Spotify user profile
    user_profile_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {spotify_access_token}"}

    user_response = get(user_profile_url, headers=headers)
    if user_response.status_code != 200:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=profile_fetch_failed")

    spotify_user = user_response.json()
    spotify_id = spotify_user.get("id")

    if not spotify_id:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=no_spotify_id")

    # Calculate token expiration time
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    # Find or create user based on the Spotify ID
    user = db.query(User).filter(User.spotify_id == spotify_id).first()

    # If no user with this Spotify ID, try to get from JWT if provided
    if not user and jwt_token:
        from src.auth import verify_token

        user_id = verify_token(jwt_token)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()

            # Link Spotify account to existing user
            if user and not user.spotify_id:
                user.spotify_id = spotify_id
                db.commit()

    # If still no user, create new account
    if not user:
        user = User(spotify_id=spotify_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Store/update token in database
    token = store_token(
        db=db,
        user_id=user.id,
        provider="spotify",
        access_token=spotify_access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

    # Generate JWT for authentication
    jwt_token = create_access_token(user.id)

    # Redirect to frontend with JWT
    return RedirectResponse(url=f"{FRONTEND_URL}?token={jwt_token}")


@app.get("/strava/login")
def strava_login(request: Request):
    """
    Redirects the user to Strava's OAuth authorization page.
    """
    # Get JWT token if it's in the request
    jwt_token = request.query_params.get("token")

    # Generate a state parameter to include the JWT token
    state = generate_random_string(16)
    if jwt_token:
        state = base64.urlsafe_b64encode(f"{state}:{jwt_token}".encode()).decode()

    STRAVA_AUTH_URL = "https://www.strava.com/oauth/authorize"
    STRAVA_SCOPE = "activity:read"

    params = {
        "client_id": STRAVA_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": STRAVA_REDIRECT_URI,
        "approval_prompt": "auto",
        "scope": STRAVA_SCOPE,
        "state": state,
    }

    return RedirectResponse(f"{STRAVA_AUTH_URL}?{urlencode(params)}")


# Add this function for decoding Strava state
def decode_strava_state(state: str):
    """
    Decode the state parameter from Strava OAuth flow

    Args:
        state: The encoded state string

    Returns:
        dict: Dictionary containing the token if present
    """
    try:
        decoded = base64.urlsafe_b64decode(state.encode()).decode()
        if ":" in decoded:
            random_str, token = decoded.split(":", 1)
            return {"token": token}
        return {}
    except Exception:
        return {}


# A Strava auth flow redirects us back here with a code in the URL
# We can exchange the code for an access token and do what we will with it.
@app.get("/strava/callback")
def strava_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handles Strava OAuth callback and creates user if not exists
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        return RedirectResponse(url=FRONTEND_URL + "/error?error=no_code")

    # Decode the state to extract any token
    decoded_state = decode_strava_state(state) if state else {}
    jwt_token = decoded_state.get("token")

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

    # Check if user exists with this Strava ID
    user = db.query(User).filter(User.strava_id == strava_id).first()

    # If no user with this Strava ID, try to get from JWT if provided
    if not user and jwt_token:
        from src.auth import verify_token

        user_id = verify_token(jwt_token)
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()

            # Link Strava account to existing user
            if user and not user.strava_id:
                user.strava_id = strava_id
                db.commit()

    # If still no user, create new account
    if not user:
        # Create new user
        user = User(strava_id=strava_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    # Store/update token
    token = store_token(
        db=db,
        user_id=user.id,
        provider="strava",
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at,
    )

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
