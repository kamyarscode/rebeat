from src.strava import build_strava_auth_url, exchange_strava_code_for_access_token
from src.helpers import decode_state
from fastapi import FastAPI, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from helpers import find_or_create_user, store_token
import os
from requests import get
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from src.db import get_db, User, Token
from src.auth import create_access_token, get_current_user
from datetime import datetime, timedelta
from src.spotify import (
    build_spotify_login_url,
    exchange_code_for_access_token,
)

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")


app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def redirect_with_error(error: str):
    return RedirectResponse(url=FRONTEND_URL + "?error=" + error)


# Root route
@app.get("/")
async def root():
    return {"message": "Welcome to Rebeat"}


# Protected endpoint to test authentication
# Returns the current authenticated user from the JWT token present in the request
@app.get("/api/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
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

    if error:
        return redirect_with_error(error)

    if not state:
        return redirect_with_error("no_state")

    if not code:
        return redirect_with_error("no_code")

    # Decode the state to extract any token
    decoded_state = decode_state(state)
    jwt_token = decoded_state.get("token")

    # Exchange the code for tokens
    token_response = exchange_code_for_access_token(code)

    if "error" in token_response or "access_token" not in token_response:
        return redirect_with_error("token_exchange_failed")

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
        return redirect_with_error("profile_fetch_failed")

    spotify_user = user_response.json()
    spotify_id = spotify_user.get("id")

    if not spotify_id:
        return redirect_with_error("no_spotify_id")

    # Calculate token expiration time
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

    user = find_or_create_user(db, "spotify", spotify_id, jwt_token)

    # Store/update token in database
    store_token(
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


# Redirects the user to Strava's OAuth authorization page.
# Includes a rebeat jwt as state to link the strava auth to the user
@app.get("/strava/login")
def strava_login(request: Request):
    jwt_token = request.query_params.get("token")
    strava_auth_url = build_strava_auth_url(token=jwt_token)
    return RedirectResponse(strava_auth_url)


# A Strava auth flow redirects us back here with a code in the URL
# We can exchange the code for an access token and do what we will with it.
# We can then either create or update a user, store their strava tokens, and redirect to the frontend with a JWT
@app.get("/strava/callback")
def strava_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code:
        return redirect_with_error("no_code")

    if not state:
        return redirect_with_error("no_state")

    # Decode the state to extract any token
    decoded_state = decode_state(state)
    jwt_token = decoded_state.get("token")

    # TODO: Check we got the requested scopes

    strava_auth = exchange_strava_code_for_access_token(code)

    # Extract Strava user ID from token response
    strava_id = str(strava_auth.athlete.id)
    access_token = strava_auth.access_token
    refresh_token = strava_auth.refresh_token
    expires_at = datetime.fromtimestamp(strava_auth.expires_at)

    user = find_or_create_user(db, "strava", strava_id, jwt_token)

    # Store/update token
    store_token(
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


# Run the app
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
