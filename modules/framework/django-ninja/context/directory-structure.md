# Django Ninja: Directory Structure

## Standard App Layout
```
apps/
└── users/
    ├── api.py             # NinjaRouters for this app
    ├── schemas.py         # Pydantic models for this app
    ├── models.py          # Django ORM models
    ├── services.py        # Business logic (used by api.py)
    └── ...
```

## Central API Mount
```
config/
├── urls.py                # Mount NinjaAPI here
└── api.py                 # Central NinjaAPI instance + router registration
```
