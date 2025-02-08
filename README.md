# Rebeat

Adds songs listened to during activities into a playlist.

[Spotify Dashboard](https://developer.spotify.com/dashboard/3127926c771c495897441b4e1a3ab7d8/settings)

Live at [rebeat.onrender.com](https://rebeat.onrender.com)

## Frontend

Vite + React + TypeScript just to send you to the auth flow and look pretty.

```bash
cd frontend
npm install
npm run dev
```

## Backend

### Set up locally

We're going to do this quick and dirty for now and migrate to Conda later.  
Clone the repo in desired directory:  
`git clone https://github.com/kamyarscode/rebeat.git`

#### Set up Python venv and install rebeat.

```bash
# Navigate to where you cloned the project
cd {dir}/rebeat/backend
# Create venv
python -m venv .rebeat
# Activate venv
.\.rebeat\Scripts\activate - Windows
OR
source .rebeat/bin/activate - Linux/MacOS
# Install project in dev mode to see changes
pip install -e .
```

If using VsCode, make sure you set the right environment when running.

#### Auth Token:

Add your auth token to a local `.env` file stored in root project directory for now.  
Example:  
`AUTH_TOKEN=B.......`

#### Start API Server:

Once env is set up, navigate to `backend/app.py` and start with VsCode or:

```bash
cd backend
python ./app.py
```

# To Do:

- Add way to support workouts longer than 100 minutes.
