# Docker Project: Flask + Redis Multi-Container App

A multi-container web application built for the CoderCo Containers Challenge, demonstrating containerization, service orchestration, and inter-container networking with Docker Compose.

## Overview

A Flask web application backed by a Redis database, running as two separate Docker containers orchestrated by Docker Compose. The app displays a welcome message and tracks the number of visits using a persistent counter stored in Redis.

**Live behavior:** every time you load the page, Flask increments a counter in Redis and displays it alongside a random quote.

## Architecture

```
                    ┌─────────────────────────────────────────┐
                    │           Docker Compose Network          │
                    │                                           │
   Browser  ──5000──▶   ┌───────────────┐      ┌─────────────┐  │
                    │   │  web (Flask)  │◀────▶│    redis    │  │
                    │   │  port 5000    │ 6379 │  port 6379  │  │
                    │   └───────────────┘      └─────────────┘  │
                    │                                           │
                    └─────────────────────────────────────────┘
```

| Container | Image | Role |
|---|---|---|
| `web` | Built from local `Dockerfile` (Python 3.12-slim) | Serves the Flask app, handles HTTP requests |
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

Then visit **http://localhost:5000** in your browser. Refresh the page to watch the visit counter climb.

To stop:

```bash
docker-compose down
```

## Design Decisions

**Combined route instead of two separate routes.** The original brief called for a static `/` route (welcome message) and a separate stateful `/count` route (visit counter). I deliberately combined both into a single `/` route so a live demo shows the welcome message *and* the incrementing counter in one page load, rather than requiring a second navigation. I understand and can explain the alternative: keeping `/` and `/count` separate is a cleaner separation-of-concerns pattern (a route with no side effects vs. one that mutates state), and I chose the combined version purely for demo presentation, not because I didn't understand the distinction.

**Port correction (5000, not 5002/5003).** An earlier draft carried over a hardcoded port (`5002`) from an unrelated project. It was corrected to `5000` so that the Flask app's `app.run(port=5000)`, the Dockerfile's `EXPOSE 5000`, and the `docker-compose.yml` port mapping (`"5000:5000"`) are all consistent. A mismatch between any of these would either break the container or make the app unreachable from the host.

## Issues Hit & Fixed

| Issue | Cause | Fix |
|---|---|---|
| Build failure | `requirements.txt` was missing | Created it with `flask` and `redis` |
| Code changes not appearing | Docker was using a cached image layer | Rebuilt with `docker-compose up --build` |
| App unreachable on expected port | Leftover port `5002` from a different project | Standardized on `5000` across `app.py`, `Dockerfile`, and `docker-compose.yml` |

## Concepts Demonstrated (Interview Notes)

**Why two containers instead of one?**
Each container should do one job — this is the single-responsibility principle applied to infrastructure. Flask and Redis have different runtimes, scaling needs, and lifecycles. Splitting them means each can be updated, restarted, or scaled independently, and the Redis image doesn't need to be modified or rebuilt just because the Flask app's code changed.

**What does `depends_on` do — and not do?**
`depends_on: [redis]` tells Docker Compose to *start* the Redis container before the `web` container. It does **not** wait for Redis to be ready to accept connections — only for the container process to have started. In a slower-starting database this can cause a race condition (the app tries to connect before Redis is actually ready). For this project, Redis starts fast enough that it isn't an issue, but a production setup would add a proper health check or retry logic.

**Why does `host='redis'` work?**
Docker Compose creates a default network for all services in the same `docker-compose.yml`, and automatically registers each service's name as a DNS hostname on that network. So `redis` isn't a fixed IP — it's a name Docker resolves internally to whichever container is running the `redis` service. This is what allows the two containers to talk to each other without hardcoded IP addresses.

**`EXPOSE` (Dockerfile) vs. `ports:` (docker-compose.yml) — what's the difference?**
- `EXPOSE 5000` in the Dockerfile is documentation/metadata: it tells anyone reading the image that the container listens on port 5000. It does **not** actually publish the port to the host machine.
- `ports: ["5000:5000"]` in `docker-compose.yml` is what actually maps a port on the host machine to a port inside the container, making the app reachable from a browser. Without this mapping, the container could still work internally (e.g., other containers could reach it), but nothing outside Docker could connect to it.

## Roadmap: Remaining Bonus Features

These are being built one at a time, deliberately, so each can be explained and defended individually rather than treated as boilerplate:

- [ ] **1. Persistent storage for Redis** — add a named Docker volume so the visit counter survives container restarts (currently resets to 0 on every restart).
- [ ] **2. Environment variables for Redis connection** — move the hardcoded `host='redis', port=6379` into environment variables, configured in `docker-compose.yml` and read via `os.environ.get(...)` in `app.py`, to demonstrate portability across environments (dev/staging/prod).
- [ ] **3. Scale + load balance the web service** — run multiple `web` container instances via `docker-compose up --scale web=3`, fronted by an NGINX reverse proxy that load-balances requests across them on a single host port.
