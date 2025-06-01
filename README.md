# Rebeat

<p align="center">
  <img src="rebeat.png"/>
</p>

Turn your runs into playlists you can revisit right from Strava. Connect your accounts to get started.

Live at [rebeat.onrender.com](https://rebeat.onrender.com)

# 📕 Table of Contents

[Quick Start](#-quick-start)
[Frontend](#frontend)  
[Backend](#backend)  
[References](#references)  
[TODO](#to-do)

## 🚀 Quick Start

You'll need postgres running locally and to setup both `.env` files.

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
npm install
npm run dev
```

## 💽 Backend

Does all the actual work with auth flows, callbacks, db storage, creating playlists, and editing activities.

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

# Pull and run a postgres container
docker-compose -p rebeat up -d

# Start the server
python ./app.py
```

> [!NOTE] VSCode Interpreter
> If using VsCode, make sure you set the right environment.
> `CMD + SHIFT + P` -> `Python: Select Interpreter` -> `.rebeat/bin/python`

> [!WARNING] Temporary Spotify Token
> Add your auth token to a local `.env` file stored in `rebeat/backend` directory for now.  
> Example:  
> `AUTH_TOKEN=B.......`

## 🔎 References

- [Spotify Dashboard](https://developer.spotify.com/dashboard/3127926c771c495897441b4e1a3ab7d8/settings)
- [Spotify API Docs](https://developer.spotify.com/documentation/web-api)
- [Strava WebHooks](https://developers.strava.com/docs/webhooks/)
- [Strava API](https://developers.strava.com/docs/reference/)

## ✅ TODO

- [ ] Use miniconda
- [ ] Add way to support workouts longer than 100 minutes
- [ ] Add a preference toggle between private/public description
- [ ] Better functionality to deliver new songs and avoid repeats
- [ ] Add map of when/where each song is played
