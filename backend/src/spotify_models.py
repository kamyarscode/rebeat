from pydantic import BaseModel
from typing import Optional


# https://developer.spotify.com/documentation/web-api/tutorials/refreshing-tokens
class RefreshSpotifyAccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
    scope: str
    expires_in: int
    refresh_token: Optional[str] = None
