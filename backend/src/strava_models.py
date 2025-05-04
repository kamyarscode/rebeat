from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime


class Athlete(BaseModel):
    id: int
    username: str
    resource_state: int
    firstname: str
    lastname: str
    bio: Optional[str] = None
    city: str
    state: str
    country: str
    sex: Literal["M", "F"]
    premium: bool
    summit: bool
    created_at: datetime
    updated_at: datetime
    badge_type_id: int
    weight: float
    profile_medium: str
    profile: str
    friend: Optional[bool] = None
    follower: Optional[bool] = None


class StravaAuthResponse(BaseModel):
    token_type: str
    expires_at: int
    expires_in: int
    refresh_token: str
    access_token: str
    athlete: Athlete


class RefreshStravaAccessTokenResponse(BaseModel):
    access_token: str
    expires_at: int
    expires_in: int
    refresh_token: str
