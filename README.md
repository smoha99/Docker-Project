# Docker Project: Flask + Redis Multi-Container App

A multi-container web application demonstrating containerisation, service orchestration, and inter-container networking with Docker Compose.

## Overview

A Flask web application backed by a Redis database, running as two separate Docker containers orchestrated by Docker Compose. The app displays a welcome message and tracks the number of visits using a persistent counter stored in Redis.

**Live behavior:** `/` shows a static welcome message. Every time you load `/count`, Flask increments a counter in Redis and displays the new total alongside a random quote.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           Docker Compose Network          │
                    │                                           │
   Browser  ──5003──▶   ┌───────────────┐      ┌─────────────┐  │
                    │   │  web (Flask)  │◀────▶│    redis    │  │
                    │   │  port 5000    │ 6379 │  port 6379  │  │
                    │   └───────────────┘      └─────────────┘  │
                    │                                           │
                    └─────────────────────────────────────────┘
```

| Container | Image | Role |
|---|---|---|
| `web` | Built from local `Dockerfile` (Python 3.12-slim) | Serves the Flask app, handles HTTP requests. Runs on container port 5000, published to host port **5003**. |
| `redis` | Official `redis` image | Stores and increments the visit counter |

The two containers communicate over the default network Docker Compose creates automatically. Flask reaches Redis using the hostname `redis` — Docker Compose's built-in DNS resolves that service name to the Redis container's internal IP, so no manual networking configuration is required.

## Tech Stack

- **Flask** — lightweight Python web framework serving the HTTP routes
- **Redis** — in-memory data store used here as a simple, fast counter
- **Docker** — containerizes each service independently
- **Docker Compose** — defines and runs the multi-container application as a single unit

## Project Structure

```
.
├── app.py               # Flask application
├── Dockerfile            # Builds the Flask (web) container image
├── docker-compose.yml    # Defines and wires together the web + redis services
├── requirements.txt      # Python dependencies (flask, redis)
└── README.md
```

## Running the App

```bash
docker-compose up --build
```

Then visit:
- **http://localhost:5003** — welcome message only
- **http://localhost:5003/count** — increments and displays the visit count

Refresh `/count` to watch the visit counter climb.

To stop:

```bash
docker-compose down
```

## Design Decisions

**Two separate routes, as the brief specifies.** `/` is a static route with no side effects — it just renders a welcome message. `/count` is a stateful route — every request increments the Redis counter and displays the new value plus a random quote. Keeping these separate is a deliberate separation-of-concerns pattern: a route that only reads/renders is easy to reason about and safe to call repeatedly (e.g. by a health check or a bot), while a route that mutates state is kept explicit and isolated.

**Port mapping (host 5003 → container 5000).** Inside the container, Flask still listens on port 5000 — that's what `app.run(port=5000)` and the Dockerfile's `EXPOSE 5000` declare, and it never needs to change. The `docker-compose.yml` port mapping `"5003:5000"` means: host port 5003 forwards to container port 5000. This is exactly why the two numbers in a `ports:` mapping don't have to match — the left side is whatever's convenient/free on your host machine, the right side must match what the app actually listens on inside the container. An earlier draft had briefly used a leftover port from an unrelated project internally, which was corrected — the internal port and `EXPOSE` must always match what `app.run()` uses, regardless of which host port you choose to publish it on.

## Issues Hit & Fixed

| Issue | Cause | Fix |
|---|---|---|
| Build failure | `requirements.txt` was missing | Created it with `flask` and `redis` |
| Code changes not appearing | Docker was using a cached image layer | Rebuilt with `docker-compose up --build` |
| App unreachable on expected port | Leftover port `5002` from a different project used internally | Standardized the internal port on `5000` across `app.py` (`app.run(port=5000)`) and the Dockerfile (`EXPOSE 5000`); the host-facing port (`5003`) is a separate, independent choice made in `docker-compose.yml`'s `ports:` mapping |

## Roadmap: Remaining Bonus Features

These are being built one at a time, deliberately, so each can be explained and defended individually rather than treated as boilerplate:

- [ ] **1. Persistent storage for Redis** — add a named Docker volume so the visit counter survives container restarts (currently resets to 0 on every restart).
- [ ] **2. Environment variables for Redis connection** — move the hardcoded `host='redis', port=6379` into environment variables, configured in `docker-compose.yml` and read via `os.environ.get(...)` in `app.py`, to demonstrate portability across environments (dev/staging/prod).
- [ ] **3. Scale + load balance the web service** — run multiple `web` container instances via `docker-compose up --scale web=3`, fronted by an NGINX reverse proxy that load-balances requests across them on a single host port.
