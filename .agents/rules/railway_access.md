# Railway Access & Database Guide

How to reach Railway services and the production PostgreSQL database.

> **Never commit credentials.** This repository is public. Read secrets from Railway at the
> moment you need them (`railway variables`, `railway run`) and keep them out of files, docs,
> commit messages and chat logs.

## Railway Environment
- **Project**: `ARJ`
- **Environment**: `production`
- **Services**: `Backend`, `Frontend`, `Postgres`, `cv-extractor-llm`
- **Frontend URL**: `https://findjobfit.de`

## Railway CLI Commands
- Status: `railway status`
- Variable names only: `railway variables --service Backend --kv | cut -d= -f1`

## Accessing the Production Database
Postgres is only reachable on Railway's private network (`postgres.railway.internal:5432`).
It has **no public TCP proxy** — do not add one.

1. Open a local tunnel (requires your Railway login and a registered SSH key):
   ```bash
   railway connect Postgres --tunnel-only -P 5433
   ```
2. Build the connection string from Railway at runtime instead of writing it down:
   ```powershell
   $pw = railway variables --service Postgres --kv | Select-String '^PGPASSWORD=' | ForEach-Object { $_.Line.Split('=',2)[1] }
   $env:DATABASE_URL = "postgresql://postgres:$pw@127.0.0.1:5433/railway"
   ```

## Running Production Migrations
With the tunnel and `$env:DATABASE_URL` from above:
```powershell
cd backend
uv run alembic upgrade head
```
Clear the variable afterwards: `Remove-Item Env:DATABASE_URL`.
