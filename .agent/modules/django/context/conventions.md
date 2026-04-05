# Django: Coding Conventions

## Python Style
- Follow **PEP 8**. Use **Black** for formatting (line length: 88).
- Use **isort** for import ordering (compatible with Black: `profile = "black"` in `setup.cfg`).
- Type-annotate all function signatures; use `from __future__ import annotations` for forward references.

## Import Order (isort groups)
1. Standard library
2. Django
3. Third-party packages
4. Local app imports

```python
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.users.models import User
```

## Naming
| Entity | Convention | Example |
|--------|-----------|---------|
| Models | `PascalCase`, singular | `UserProfile`, `Order` |
| Model fields | `snake_case` | `created_at`, `is_active` |
| Views (CBV) | `PascalCase` + View suffix | `UserListView`, `OrderDetailView` |
| Views (FBV) | `snake_case` | `user_list`, `order_detail` |
| URL names | `<app>:<resource>-<action>` | `users:profile-detail` |
| Templates | `<app>/<model>_<action>.html` | `users/profile_detail.html` |
| Forms/Serializers | `PascalCase` + suffix | `UserCreateSerializer`, `LoginForm` |
| Signal handlers | `on_<model>_<signal>` | `on_user_post_save` |
| Management commands | `snake_case` (filename) | `sync_external_users.py` |

## Models
- Always define `__str__` returning a human-readable string.
- Always define `class Meta` with at least `verbose_name` and `verbose_name_plural`.
- Use `gettext_lazy as _` for all string literals in models (i18n-ready).
- Use `UUIDField` as primary key for public-facing models instead of auto-increment integer.
- Always add `db_index=True` or `unique=True` explicitly — don't rely on FK implicit indexes for query-heavy fields.

```python
class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("user profile")
        verbose_name_plural = _("user profiles")

    def __str__(self) -> str:
        return f"Profile({self.user.email})"
```

## Migrations
- Never hand-edit migration files unless correcting a squash or circular dependency.
- Always run `makemigrations` with a descriptive name: `python manage.py makemigrations users --name add_bio_to_profile`.
- Review generated migration files before committing — check for unexpected `AlterField` or table renames.
- Never run `migrate` directly in production without a rollback plan.
