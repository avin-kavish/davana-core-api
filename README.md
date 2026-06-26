# Davana Core API

Django backend for the Davana vehicle listings platform.

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)
- External PostgreSQL database

## Setup

```bash
cp .env.example .env
# Edit .env with your database credentials and secret key

source source-env.sh
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

## Environment variables

### Application

| Variable | Description |
| -------- | ----------- |
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `true` or `false` |
| `ALLOWED_HOSTS` | Comma-separated hostnames |

### Database (`CORE_DATA_*`)

| Variable | Description |
| -------- | ----------- |
| `CORE_DATA_HOST` | Postgres host |
| `CORE_DATA_PORT` | Postgres port (default `5432`) |
| `CORE_DATA_NAME` | Database name |
| `CORE_DATA_USER` | Database user |
| `CORE_DATA_PASSWORD` | Database password |
| `CORE_DATA_SSLMODE` | SSL mode (default `prefer`) |

### Azure Blob Storage (optional)

When `AZURE_ACCOUNT_NAME` is set, images upload to Azure. Otherwise files are stored under `media/`.

| Variable | Description |
| -------- | ----------- |
| `AZURE_ACCOUNT_NAME` | Storage account name |
| `AZURE_ACCOUNT_KEY` | Storage account key |
| `AZURE_CONTAINER` | Container name (default `davana`) |

## API

Read-only endpoints under `/v1/`:

```bash
curl http://127.0.0.1:8000/v1/vehicles/
curl http://127.0.0.1:8000/v1/vehicles/{short_id}/
curl http://127.0.0.1:8000/v1/sellers/
curl http://127.0.0.1:8000/v1/sellers/1/
```

Vehicle detail returns a `seller` id only; fetch the seller profile from `/v1/sellers/{id}/`.

Supported list filters: `vehicle_type`, `make`, `model`, `year_from`, `year_to`, `price_from`, `price_to`, `mileage_from`, `mileage_to`, `condition`, `registration`, `color`, `fuel`, `transmission`, `hybrid`.

## Tests

```bash
uv run python manage.py test
```

Tests use SQLite automatically. Production uses Postgres when `CORE_DATA_HOST` is set in `.env`; without it, local commands also fall back to SQLite.

## Admin

Django admin is available at `/admin/` with support for vehicle photo uploads.
