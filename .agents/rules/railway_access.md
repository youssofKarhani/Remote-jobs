# Railway Access & Database Guide

This rule documents how to access Railway services and the production PostgreSQL database for `youssofKarhani/Remote-jobs`.

## Railway Environment
- **Project**: `ARJ` (`f942086f-01fd-485c-a39f-204dbf631680`)
- **Environment**: `production` (`df8fc9d1-fffa-48bb-98f2-2af53105df7f`)
- **Backend Service**: `Backend` (`281f9e6b-0993-4f55-839e-cb59a9403343`)
- **Postgres Database**: `Postgres` (`44de9d0d-0d40-4aa4-9b23-b614bafc0d9d`)
- **Frontend URL**: `https://frontend-production-a50a.up.railway.app`

## Railway CLI Commands
- Status: `railway status`
- Variables: `railway variables list --service Backend` / `railway variables list --service Postgres`

## Accessing Production Postgres DB via SSH Tunnel
The database host is `postgres.railway.internal:5432`. To access it from local:

1. **Local SSH Key**: `C:\Users\USER\.ssh\id_ed25519` (registered with `railway ssh keys add`).
2. **Start Local Tunnel**:
   ```bash
   railway connect Postgres --tunnel-only -P 5433
   ```
3. **Database URL over Tunnel**:
   ```text
   postgresql://postgres:OgkamCHQMaJeQIcITkwEpZsftqsONKNp@127.0.0.1:5433/railway
   ```

## Running Production Migrations
```powershell
$env:DATABASE_URL="postgresql://postgres:OgkamCHQMaJeQIcITkwEpZsftqsONKNp@127.0.0.1:5433/railway"
uv run alembic upgrade head
```
