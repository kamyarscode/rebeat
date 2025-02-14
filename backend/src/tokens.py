user_tokens = {"strava": {}, "spotify": {}}


def refresh_tokens(access_token, refresh_token):
    # Refresh the tokens starter code
    tokens = {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

    return tokens