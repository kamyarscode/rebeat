# Rebeat

Adds songs listened to during activities into a playlist.

# Table of Contents:
[Access](#access)  
[Frontend](#frontend)  
[Backend](#backend)  
[References](#references)  
[To Do](#to-do)  

## Access:
[Spotify Dashboard](https://developer.spotify.com/dashboard/3127926c771c495897441b4e1a3ab7d8/settings)

Live at [rebeat.onrender.com](https://rebeat.onrender.com)

Use `./dev.sh` to run the backend and frontend concurrently.

## Frontend

Vite + React + TypeScript just to send you to the auth flow and look pretty.

```bash
cd frontend
npm install
npm run dev
```

## Backend:

### Set up locally:

We're going to do this quick and dirty for now and migrate to Conda later.  
Clone the repo in desired directory:  
`git clone https://github.com/kamyarscode/rebeat.git`

#### Set up Python venv and install rebeat:

```bash
# Navigate to the backend directory
cd ./backend

# Create venv
python -m venv .rebeat

# Activate venv (Windows)
.\.rebeat\Scripts\activate
# OR Activate venv (Linux/MacOS)
source .rebeat/bin/activate

# Install project in dev mode to see changes
pip install -e .
```

If using VsCode, make sure you set the right environment when running.
`CMD + SHIFT + P` -> `Python: Select Interpreter` -> `.rebeat/bin/python`

#### Auth Token:

Add your auth token to a local `.env` file stored in `rebeat/backend` directory for now.  
Example:  
`AUTH_TOKEN=B.......`

#### Start API Server:

Once env is set up, navigate to `backend/app.py` and start with VsCode or:

```bash
cd backend
python ./app.py
```

## References:
[Spotify API Docs](https://developer.spotify.com/documentation/web-api)  
[Strava WebHooks](https://developers.strava.com/docs/webhooks/)  
[Strava API](https://developers.strava.com/docs/reference/)  

## To Do:

- Add way to support workouts longer than 100 minutes.
- Add option for user to add notes to private/public notes.
