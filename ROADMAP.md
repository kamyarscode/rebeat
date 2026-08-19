# Roadmap

Where rebeat is headed, and what's known about the constraints. Written 2026-08-19.

## Goal

Replace the user-triggered "add a playlist" button — always a prototype — with a
**Strava webhook** that enhances every activity automatically on upload.

This is also the real fix for the history-horizon problem: generating minutes
after upload keeps every activity inside Spotify's 50-track buffer, so
`horizon_exceeded` becomes rare instead of routine.

## Done

| PR | What |
|---|---|
| [#2](https://github.com/kamyarscode/rebeat/pull/2) | History horizon: distinguish "no songs played" from "run too old to know". Also fixed the ISO-string-as-`before` cursor, the missing `limit` (capped at 20, not 50), the absent upper bound, track ordering, and window padding |
| [#3](https://github.com/kamyarscode/rebeat/pull/3) | Clean 404/502 instead of `IndexError`/`KeyError: 0`; `compose_description` stops writing literal `"None"` onto activities |
| [#4](https://github.com/kamyarscode/rebeat/pull/4) | Remove dead `with_auth_headers`/`AUTH_TOKEN`; fix README setup commands that never worked |

Time handling is now uniformly UTC milliseconds end to end. **No timing or
unit-conversion bugs remain.**

## Corrections to earlier analysis

Recorded because they were stated as fact earlier and are wrong:

- **Token refresh is not a time bug.** All writes are naive (`datetime.now()` /
  `datetime.fromtimestamp()`) and all reads compare naive against naive. That's
  self-consistent on one server, and Vercel runs UTC. Fragile, not broken.
- **`played_at` is not reliably the end of playback.** Undocumented and
  [reported inconsistent](https://github.com/spotify/web-api/issues/1083).
  Hence padding the window rather than subtracting `duration_ms`.
- **Back-dated uploads are not a silent wrong-activity bug.** `GET`/`POST
  /latest` share a selection, so the UI names the target before you click.
  There is also no upload-time field on Strava's activity models to sort by.

## Remaining bugs

1. **Errors that lie** — `create_playlist`/`add_songs` return `{"error": ...}`
   on failure, which gets concatenated onto a URL string: a `TypeError` dressed
   as a playlist. The `PUT` writing the description is unchecked. *Do first —
   it's what will obscure any failure in the untested happy path.*
2. **`strava_models.Athlete` is over-strict** — `username`, `city`, `state`,
   `country`, `sex: Literal["M","F"]` are required but nullable in Strava's
   responses. Sparse profiles get a `ValidationError` → 500 on
   `/strava/callback` and cannot sign up. *Blocks new users; promote above #1
   before any real launch.*
3. **No idempotency** — clicking twice creates two playlists and appends two
   URLs.
4. **Missing token rows** `AttributeError` instead of prompting a reconnect.

## Webhook work

- `backend/src/strava_webook.py` is entirely commented out; the endpoints are
  sketched but unwired (note the filename typo).
- Needs: subscription lifecycle, `GET` verification echo (`hub.challenge`),
  `POST` event handling, dedupe on `object_id`, and auth — webhook events carry
  a Strava athlete id, not a rebeat JWT, so users must be resolvable by
  `strava_id`.
- Idempotency (bug #3) becomes load-bearing here: Strava retries.

## Open design question

Once enhancement is automatic, we need to know which activities are already
done. Two options:

1. **Persist to our DB** — an `enhanced_activities` table. Authoritative, cheap
   to query, survives playlist deletion. Another table to migrate and keep in
   sync.
2. **Query Spotify live** — list the user's playlists, look for the Strava link.
   No schema, always reflects reality. Costs an API call, is paginated, and
   breaks if a user renames or deletes a playlist.

Leaning (1) for correctness with (2) as a possible reconciliation pass. Undecided.

## Constraints worth not rediscovering

- Spotify `recently-played` holds **exactly 50 items**; the 51st evicts the
  oldest permanently. Verified: paging before the oldest returns zero items and
  no cursors. Cursors cannot page outside the buffer, which is why we fetch the
  whole thing and filter locally.
- One real account's buffer spanned **~14.5 hours**.
- `limit` max is 50, enforced with a 400.
- The response's `next` field is non-null even when following it yields nothing.
- Strava `/athlete/activities` has **no** server-side type filter — only
  `before`, `after`, `page`, `per_page`.

## Deferred: simplify the Vercel deployment

Current shape: `api/[[...path]].py` is a shim that `sys.path`-hacks its way to
`backend/app.py`, plus two rewrites in `vercel.json`.

**Renaming `backend/` to `api/` does not help — it breaks things.** Without a
framework preset, every `.py` under `/api` becomes its own function served at
its file path, so `api/src/db.py` would be an endpoint at `/api/src/db`, as
would every file in `api/tests/`. Internals addressable over HTTP, functions
wasted, most without a top-level `app`/`handler`.

**The rewrites are load-bearing, not cruft.** The `[[...path]]` bracket syntax
is a Next.js convention; Vercel's Python file-based routing serves each file at
its literal path, so that shim is otherwise only reachable at the literal URL
`/api/[[...path]]`. FastAPI's routes are already declared as `/api/...`, so the
function receives the full path and matches directly — no prefix stripping.

**The real simplification** is the FastAPI framework preset, which takes
precedence over file-based functions and makes the app handle all routing:

```toml
# backend/pyproject.toml
[tool.vercel]
entrypoint = "backend.app:app"
```

That deletes the shim, the `sys.path` hack, and both rewrites. The catch: the
preset routes *every* request to FastAPI, so the Vite frontend needs a new home
— either `app.frontend("/", directory="dist")` (Vercel promotes to the CDN at
build time) or [Services](https://vercel.com/docs/services), Vercel's documented
answer for a Python backend and a frontend in one project.

**Deliberately deferred.** The current setup works and is ~10 lines of config.
Migrating changes deployment topology and touches the OAuth redirect URIs, which
are the thing that breaks loudly and blocks signups. Do it when the `sys.path`
hack actually hurts — plausibly when the webhook adds a second entrypoint — and
do it behind a preview deploy.

Related: `requirements.txt` duplicates the dependencies in
`backend/pyproject.toml` and can drift. The framework preset would make
pyproject the single source.

## Also outstanding

- **The happy path has never run in production.** Only the 410 has been seen
  live. Covered by 29 tests and a stubbed end-to-end run, but never against real
  Spotify data.
- Deliberately deferred: frontend eligibility gating (judged over-engineering),
  activity-type filtering (works fine on rides), supporting >50 songs (a hard
  Spotify limit).
