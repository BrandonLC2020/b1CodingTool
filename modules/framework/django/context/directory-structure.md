# Django: Directory Structure

## Recommended Layout

```
project_root/
├── manage.py
├── pyproject.toml             # or setup.cfg — project metadata + tool config
├── requirements/
│   ├── base.txt               # Shared dependencies
│   ├── dev.txt                # -r base.txt + debug tools, pytest, factory-boy
│   └── prod.txt               # -r base.txt + gunicorn, sentry-sdk
├── config/                    # Django project package (replaces the default <projectname>/ dir)
│   ├── __init__.py
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── dev.py             # DEBUG=True, local DB, etc.
│   │   └── prod.py            # Secure settings, env-var driven
│   ├── urls.py                # Root URL conf — includes each app's urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/                      # All Django apps live here
│   ├── core/                  # Shared abstract models, utilities, base views
│   │   ├── models.py          # TimeStampedModel, UUIDModel abstract bases
│   │   └── utils.py
│   ├── users/
│   │   ├── __init__.py
│   │   ├── apps.py            # AppConfig — register signals in ready()
│   │   ├── admin.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py     # DRF serializers
│   │   ├── urls.py            # App-level URL patterns
│   │   ├── services.py        # Business logic (optional, use when models get fat)
│   │   ├── signals.py         # Signal handlers
│   │   ├── migrations/
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── factories.py   # factory_boy factories for this app
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       └── test_serializers.py
│   └── orders/
│       └── ...                # Same structure as users/
├── templates/                 # Global templates (app templates go in apps/<app>/templates/<app>/)
│   └── base.html
├── static/                    # Static files collected here by collectstatic
└── .env                       # Local secrets — never commit
```

## Settings Strategy
Split settings using environment variable `DJANGO_SETTINGS_MODULE`:

```python
# config/settings/base.py — shared across all environments
INSTALLED_APPS = [
    "django.contrib.auth",
    ...
    "rest_framework",
    "apps.core",
    "apps.users",
]

# config/settings/dev.py
from .base import *
DEBUG = True
DATABASES = {"default": env.db("DATABASE_URL", default="sqlite:///db.sqlite3")}

# config/settings/prod.py
from .base import *
DEBUG = False
DATABASES = {"default": env.db("DATABASE_URL")}
SECURE_SSL_REDIRECT = True
```

## App Registration
Register each app with a custom `AppConfig` in `apps.py`:

```python
# apps/users/apps.py
from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = "apps.users"
    verbose_name = "Users"

    def ready(self) -> None:
        import apps.users.signals  # noqa: F401
```

In `INSTALLED_APPS` use: `"apps.users.apps.UsersConfig"` (not just `"apps.users"`).

## URL Structure
```python
# config/urls.py
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/users/", include("apps.users.urls", namespace="users")),
    path("api/orders/", include("apps.orders.urls", namespace="orders")),
]

# apps/users/urls.py
app_name = "users"
urlpatterns = [
    path("", UserListView.as_view(), name="user-list"),
    path("<uuid:pk>/", UserDetailView.as_view(), name="user-detail"),
]
```

## Key Files Reference
| File | Purpose |
|------|---------|
| `config/settings/base.py` | Shared settings |
| `apps/core/models.py` | `TimeStampedModel`, `UUIDModel` abstract bases — inherit everywhere |
| `apps/<app>/services.py` | Business logic that doesn't belong on models |
| `apps/<app>/tests/factories.py` | `factory_boy` factories for test data |
| `.env` | Local secrets (never commit) |
