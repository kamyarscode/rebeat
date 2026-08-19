# Rebeat

<p align="center">
  <img src="rebeat.png"/>
</p>

Turn your runs into playlists you can revisit right from Strava. Connect your accounts to get started.

Live at [rebeat.cutaiar.io](https://rebeat.cutaiar.io) (deployed on Vercel; previously on Render)

# 📕 Table of Contents

[Quick Start](#-quick-start)
[Frontend](#frontend)  
[Backend](#backend)  
[References](#references)  
[TODO](#to-do)

## 🚀 Quick Start

You'll need docker, python, and bun.

```sh
# Clone the repo
git clone https://github.com/kamyarscode/rebeat.git

# Run the backend and frontend concurrently
./dev.sh
```

## 🌐 Frontend

Vite + React + TypeScript just to send you to the auth flow and look pretty.

```bash
cd frontend

# Copy the example env and update with the right values
cp example.env .env

# install deps and run dev server
bun install
bun run dev
```

## 💽 Backend

Does all the actual work with auth flows, callbacks, db storage, creating playlists, and editing activities.

```bash


# Navigate to the backend directory
cd ./backend

# Copy the example env and update with the right values
cp .example.env .env

# Create venv
python -m venv .rebeat

# Activate venv (Windows)
.\.rebeat\Scripts\activate
# OR Activate venv (Linux/MacOS)
source .rebeat/bin/activate

# Install project in dev mode to see changes
pip install -e .

# Pull and run a local postgres container
# (or skip this and point DATABASE_URL at a hosted database instead)
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

> [!NOTE] Database connection
> `DATABASE_URL` takes precedence if set; otherwise the `DB_*` variables are
> used to build a connection string for the local container above.

## 🔎 References

- [Spotify Dashboard](https://developer.spotify.com/dashboard/3127926c771c495897441b4e1a3ab7d8/settings)
- [Spotify API Docs](https://developer.spotify.com/documentation/web-api)
- [Strava WebHooks](https://developers.strava.com/docs/webhooks/)
- [Strava API](https://developers.strava.com/docs/reference/)

## ✅ TODO

- [ ] Use uv
- [x] If there's no content to create newlines after, don't
- [ ] Generate an image for the playlist based on the run and songs?
- [x] Reverse the order of songs added so that the first songs in the playlist are the first ones on the run
- [x] Throw if there no no songs during the run and surface on frontend
- [ ] Organize playlists under a folder
- [ ] UI showing the latest activities, if they've been enhanced, and a button to do so
- [ ] Add way to support workouts longer than 100 minutes / more than 50 songs
- [ ] Add a preference toggle between private/public description
- [ ] Add map of when/where each song is played
