# Rebeat

<p align="center">
  <img src="rebeat.png"/>
</p>

Turn your runs into playlists you can revisit right from Strava. Connect your accounts to get started.

Live at [rebeat.cutaiar.io](https://rebeat.cutaiar.io)

# 📕 Table of Contents

[Quick Start](#-quick-start)  
[Frontend](#-frontend)  
[Backend](#-backend)  
[Deployment](#-deployment)  
[References](#-references)  
[Roadmap](ROADMAP.md)

## 🚀 Quick Start

You'll need docker, python, bun, and the vercel cli.

```sh
# Prerequisites
brew install vercel
brew install oven-sh/bun/bun
# install python and docker your way

# Clone
git clone https://github.com/Cutaiar/rebeat.git
cd rebeat

# Link to the Vercel project and pull the backend secrets into backend/.env
vercel link
vercel env pull backend/.env

# Point the backend at the local database instead of production Neon.
# Every pull restores the production value, so redo this after re-pulling.
echo 'DATABASE_URL=postgresql://postgres:password@localhost:5432/rebeat' >> backend/.env
```

That covers the backend. The frontend needs one variable of its own — both
one-time setups are below. After that, `./dev.sh` runs the two servers together
(it does not start the database).

## 🌐 Frontend

Vite + React + TypeScript just to send you to the auth flow and look pretty.

```bash
cd frontend

# VITE_API_URL=http://localhost:8000 for local dev
cp example.env .env

# install deps and run dev server
bun install
bun run dev
```

## 💽 Backend

Does all the actual work with auth flows, callbacks, db storage, creating playlists, and editing activities.

```bash
cd ./backend

# Create and activate venv (Linux/macOS; use .\.rebeat\Scripts\activate on Windows)
python3 -m venv .rebeat
source .rebeat/bin/activate

# Install project in dev mode to see changes
pip install -e .

# Pull and run a local postgres container (skip if using a hosted DATABASE_URL)
docker-compose -p rebeat up -d

# Start the server
python ./app.py

# Run the tests
pip install -e ".[dev]"
pytest
```

> [!NOTE] VSCode Interpreter
> If using VsCode, make sure you set the right environment.
> `CMD + SHIFT + P` -> `Python: Select Interpreter` -> `.rebeat/bin/python`

## 🚢 Deployment

Deployed on Vercel (previously on Render). Pushes to `main` deploy to
production.

`api/[[...path]].py` is a shim that hands every `/api/*` request to the FastAPI
app in `backend/`, wired up by the rewrites in `vercel.json`. Root
`requirements.txt` is what Vercel installs. See [ROADMAP.md](ROADMAP.md) for why
it is shaped this way.

## 🔎 References

- [Spotify Dashboard](https://developer.spotify.com/dashboard/3127926c771c495897441b4e1a3ab7d8/settings)
- [Spotify API Docs](https://developer.spotify.com/documentation/web-api)
- [Strava WebHooks](https://developers.strava.com/docs/webhooks/)
- [Strava API](https://developers.strava.com/docs/reference/)
