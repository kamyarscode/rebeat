# Vercel Migration

Migrating rebeat off Render (paid Postgres + free web/static) onto Vercel (free) + Neon (free Postgres).

## What changed in this branch

- **Root `vercel.json`** — builds frontend with bun, serves `frontend/dist`, rewrites `/api/*` to the Python function.
- **Root `api/index.py`** — shim that imports the FastAPI `app` from `backend/app.py`.
- **Root `requirements.txt`** — deps for the Python function (Vercel's Python runtime reads this).
- **`backend/app.py`** — all routes prefixed with `/api` (`/spotify/callback` → `/api/spotify/callback`, etc). Required by the rewrite.
- **`backend/src/db.py`** — accepts `DATABASE_URL` env var directly (Neon-style), reduced pool size for serverless, removed `create_database` startup call.

## Deploy checklist

### 1. Provision Neon Postgres

In the Vercel dashboard → Storage → Create → Neon (via Marketplace, free tier).
It auto-wires `DATABASE_URL` + `POSTGRES_*` vars into the project.

### 2. Migrate data from Render → Neon

```sh
# Get the Render external connection string from the Render dashboard
# Get the Neon direct (non-pooled) URL from Vercel → Storage → your DB → .env.local

pg_dump "$RENDER_URL" --no-owner --no-acl -f rebeat.sql
psql "$NEON_DIRECT_URL" -f rebeat.sql
```

Use the **pooled** URL for `DATABASE_URL` in Vercel env (better for serverless).
Use the **direct** URL for the one-time `psql` restore above.

### 3. Set env vars in Vercel

Copy from current Render backend service:
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`
- `STRAVA_CLIENT_ID`, `STRAVA_CLIENT_SECRET`
- `JWT_SECRET` (whatever `src/auth.py` reads)
- `FRONTEND_URL` — set to the Vercel production URL (e.g. `https://rebeat.vercel.app`)

Frontend env:
- `VITE_API_URL=/api` — same-origin, no CORS needed.

### 4. Update OAuth redirect URIs

Route paths gained an `/api` prefix. Update in each provider dashboard:

- **Spotify** → Developer Dashboard → app → Redirect URIs
  - Old: `https://rebeat-backend.onrender.com/spotify/callback`
  - New: `https://<vercel-url>/api/spotify/callback`
- **Strava** → API settings → Authorization Callback Domain
  - Set to your Vercel domain

### 5. Deploy

Push branch → connect repo in Vercel → deploy. First push creates a preview URL; promote to production once verified.

### 6. Verify

- Hit `https://<vercel-url>/api` — should return `{"message":"Welcome to Rebeat"}`
- Try the full Spotify + Strava login flow
- Check Vercel function logs for cold-start times and errors

### 7. Cancel Render

Once verified end-to-end for a day or two:
- Delete `rebeat-db` (Postgres, ~$6/mo)
- Delete `rebeat-frontend` and `rebeat-backend` services
- Confirm no active billing on Render account

## Known trade-offs

- **10s function timeout on Hobby.** Callbacks fit; if `add_playlist_to_latest_run` ever blows past 10s (Strava + Spotify sequential calls), bump to Pro or split into async work.
- **Cold starts** (~1–2s Python + ~500ms Neon wake) on the first request after idle.
- **Schema creation** still runs on cold start via `Base.metadata.create_all` at module import. Idempotent, so fine — but you can pre-run it once locally against Neon and remove that line if you want faster cold starts.
