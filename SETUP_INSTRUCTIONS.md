# SafeSignal Backend — Setup Instructions

## 1. Create the project structure
```bash
django-admin startproject safesignal
cd safesignal
python manage.py startapp accounts
python manage.py startapp incidents
```

## 2. Drop the generated files into place

| Generated file | Destination |
|---|---|
| `settings.py` | `safesignal/safesignal/settings.py` (overwrite) |
| `urls.py` | `safesignal/safesignal/urls.py` (overwrite) |
| `asgi.py` | `safesignal/safesignal/asgi.py` (overwrite) |
| `celery.py` | `safesignal/safesignal/celery.py` (new) |
| `accounts_models.py` | `safesignal/accounts/models.py` |
| `accounts_serializers.py` | `safesignal/accounts/serializers.py` |
| `accounts_views.py` | `safesignal/accounts/views.py` |
| `accounts_urls.py` | `safesignal/accounts/urls.py` |
| `incidents_models.py` | `safesignal/incidents/models.py` |
| `incidents_serializers.py` | `safesignal/incidents/serializers.py` |
| `incidents_views.py` | `safesignal/incidents/views.py` |
| `incidents_tasks.py` | `safesignal/incidents/tasks.py` |
| `incidents_consumers.py` | `safesignal/incidents/consumers.py` |
| `incidents_routing.py` | `safesignal/incidents/routing.py` |
| `incidents_urls.py` | `safesignal/incidents/urls.py` |
| `requirements.txt` | `safesignal/requirements.txt` |
| `.env.example` | `safesignal/.env` (fill in real values) |

Add this to `safesignal/safesignal/__init__.py`:
```python
from .celery import app as celery_app
__all__ = ("celery_app",)
```

## 3. Install dependencies
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```
GDAL/GEOS are required for `django.contrib.gis` — on Ubuntu: `sudo apt install gdal-bin libgdal-dev`.

## 4. Database (PostGIS)
```bash
# using Docker for local Postgres+PostGIS:
docker run -d --name safesignal-db -e POSTGRES_USER=safesignal \
  -e POSTGRES_PASSWORD=safesignal -e POSTGRES_DB=safesignal \
  -p 5432:5432 postgis/postgis
```

## 5. Redis (for Channels + Celery)
```bash
docker run -d --name safesignal-redis -p 6379:6379 redis
```

## 6. Migrate + run
```bash
python manage.py makemigrations accounts incidents
python manage.py migrate
python manage.py createsuperuser
daphne -p 8000 safesignal.asgi:application     # instead of runserver, for WebSocket support
celery -A safesignal worker -l info             # in a second terminal
```

## 7. Quick test flow
1. `POST /api/auth/register/` → create a user
2. `POST /api/auth/login/` → get JWT access token
3. `PATCH /api/auth/me/` with `lat`/`lng` → set your location
4. `POST /api/incidents/` with `type`, `description`, `lat`, `lng` → raise SOS (AI triage + broadcast fire automatically)
5. `GET /api/incidents/nearby/?lat=..&lng=..&radius=5000` → see it show up
6. Connect a WebSocket client to `ws://localhost:8000/ws/notifications/` to receive the live broadcast

This covers the MVP backend spine (Section 11 of the blueprint). Next: build the React SOS button + map screen against these endpoints.
