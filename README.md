# CounterFlow: Flask + Redis Multi-Container App

A multi-container web application built for the CoderCo Containers Challenge, demonstrating containerisation, service orchestration, persistent storage, environment-based configuration, and load balancing with Docker Compose.

## Overview

A Flask web application backed by a Redis database, fronted by an NGINX reverse proxy, running as three orchestrated Docker containers. The app displays a welcome message, tracks visits with a Redis-backed counter, and includes an About page.

**Live behavior:** `/` shows a static welcome message. Every time you load `/count`, Flask increments a counter in Redis and displays the new total alongside a random quote. `/about` shows a short bio.

## Architecture

```
                              ┌───────────────────────────────────────────────────┐
                              │                 Docker Compose Network              │
                              │                                                     │
   Browser  ──5003──▶  nginx │──▶  ┌───────────────┐      ┌─────────────┐          │
                              │     │  web (Flask)  │◀────▶│    redis    │          │
                              │     │  port 5000    │ 6379 │  port 6379  │          │
                              │     └───────────────┘      └─────────────┘          │
                              │                                    │                │
                              │                              [redis-data volume]     │
                              └───────────────────────────────────────────────────┘
```

| Container | Image | Role |
|---|---|---|
| `nginx` | Official `nginx` image | Reverse proxy — the single entry point on host port **5003**, forwards requests to `web` |
| `web` | Built from local `Dockerfile` (Python 3.12-slim) | Serves the Flask app on container port 5000 (not published directly to the host) |
| `redis` | Official `redis` image | Stores and increments the visit counter, backed by a named volume for persistence |

Containers communicate over the default network Docker Compose creates automatically. Flask reaches Redis using the hostname `redis`, and NGINX reaches Flask using the hostname `web` — Docker Compose's built-in DNS resolves each service name to that container's internal IP, so no manual networking configuration is required.

## Tech Stack

- **Flask** — lightweight Python web framework serving the HTTP routes, using Jinja templates (`render_template`) for HTML
- **Redis** — in-memory data store used here as a simple, fast, persistent counter
- **NGINX** — reverse proxy sitting in front of Flask
- **Docker** — containerizes each service independently
- **Docker Compose** — defines and runs the multi-container application as a single unit

## Project Structure

```
.
├── app.py                 # Flask application
├── Dockerfile              # Builds the Flask (web) container image
├── docker-compose.yml      # Defines and wires together web + redis + nginx
├── nginx.conf              # NGINX reverse proxy configuration
├── requirements.txt        # Python dependencies (flask, redis)
├── templates/
│   ├── index.html          # Welcome page
│   ├── count.html          # Visit counter page
│   └── about.html          # About page
└── README.md
```

## Running the App

```bash
docker-compose up --build
```

Then visit:
- **http://localhost:5003** — welcome message
- **http://localhost:5003/count** — increments and displays the visit count
- **http://localhost:5003/about** — about page

To stop:

```bash
docker-compose down
```

To scale the Flask service behind NGINX:

```bash
docker-compose up --scale web=3
```

## Design Decisions

**Two separate routes, as the brief specifies.** `/` is a static route with no side effects — it just renders a welcome message. `/count` is a stateful route — every request increments the Redis counter and displays the new value plus a random quote. Keeping these separate is a deliberate separation-of-concerns pattern: a route that only reads/renders is easy to reason about and safe to call repeatedly (e.g. by a health check or a bot), while a route that mutates state is kept explicit and isolated.

**NGINX as the single entry point.** Rather than publishing the Flask container's port directly to the host, only `nginx` publishes a host port (5003). `web` uses `expose` instead of `ports`, meaning it's reachable by other containers on the same Docker network but not directly from the host machine. This is what makes scaling possible: multiple `web` replicas can all listen on port 5000 internally without fighting over a host port, since NGINX is the only container touching the host.

**Persistent Redis storage.** Redis normally stores its data inside the container's own filesystem, which is wiped when the container is removed. Mounting a named volume (`redis-data:/data`) means the visit count survives container restarts.

**Environment variables for Redis connection.** `REDIS_HOST` and `REDIS_PORT` are set in `docker-compose.yml` and read in `app.py` via `os.getenv(...)`, instead of being hardcoded. This makes the app portable across environments without code changes.

## Issues Hit & Fixed

| Issue | Cause | Fix |
|---|---|---|
| Build failure | `requirements.txt` was missing | Created it with `flask` and `redis` |
| Code changes not appearing | Docker was using a cached image layer | Rebuilt with `docker-compose up --build` |
| App unreachable on expected port | Leftover port `5002` from a different project used internally | Standardized the internal port on `5000` across `app.py` (`app.run(port=5000)`) and the Dockerfile (`EXPOSE 5000`) |
| Visit count reset on restart | Redis had no persistent storage | Added a named volume (`redis-data:/data`) |
| Scaling broke with a fixed host port | Multiple `web` containers can't all bind to the same host port | Removed the host port mapping from `web`, added NGINX as a reverse proxy publishing the single host port instead |
