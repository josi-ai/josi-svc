---
description: How to start the Josi local development server (backend + frontend)
---
// turbo-all

# Starting the Josi Dev Server

## Overview
The Josi platform uses a custom CLI (`josi`) for managing development services. The `josi redock` command handles Docker Compose services (API, database, Redis) and the Next.js frontend dev server together.

## Command

```bash
josi redock up dev --local
```

This starts:
- **Backend API** (Docker container `josi-api` on port 1954)
- **PostgreSQL** (Docker container `josi-db` on port 1961)
- **Redis** (Docker container `josi-svc-redis-1` on port 6399)
- **Next.js frontend** (local process on port 1989, using Turbopack)

### Options
| Flag | Description |
|------|-------------|
| `--local` | Use local database instead of Cloud SQL |
| `-d, --detach` | Run in background and return the prompt |
| `--no-web` | Skip starting the frontend (backend only) |
| `--no-build` | Skip rebuilding Docker images |

### Common Variants
```bash
# Full stack, foreground (Ctrl+C to stop all)
josi redock up dev --local

# Full stack, background
josi redock up dev --local -d

# Backend only (no frontend)
josi redock up dev --no-web

# Cloud DB + local frontend
josi redock up dev
```

## Other Useful Commands

```bash
# Check running container status
josi redock status

# Follow container logs
josi redock logs [service]

# Stop all containers (optionally remove volumes)
josi redock clean

# Validate Docker and project setup
josi redock check
```

## Important Notes
- The frontend runs on **port 1989** (http://localhost:1989)
- The API runs on **port 1954** (http://localhost:1954)
- Do NOT manually start the Next.js server with `npx next dev` — always use `josi redock up dev --local`
- If the frontend needs a restart, stop the current process and re-run the command
- The `.next` cache can be cleared with `rm -rf web/.next` if HMR issues arise
