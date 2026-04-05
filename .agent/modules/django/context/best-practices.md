# Django: Best Practices

## Models & ORM
- **Fat models, thin views.** Business logic belongs in model methods, managers, or a dedicated `services.py` — not in views.
- Use **custom managers** to encapsulate common querysets:

```python
class ActiveUserManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_active=True)

class User(AbstractUser):
    active = ActiveUserManager()
```

- Always use `select_related()` for `ForeignKey`/`OneToOneField` traversals and `prefetch_related()` for `ManyToManyField`/reverse FKs to avoid N+1 queries.
- Never call `.all()` in a view without a subsequent `.filter()` or `.select_related()`.
- Use `.only()` or `.defer()` to exclude heavy fields (e.g., large `TextField`) when full objects aren't needed.
- Wrap multi-step DB operations in `transaction.atomic()`.

```python
from django.db import transaction

@transaction.atomic
def transfer_credits(sender: User, recipient: User, amount: int) -> None:
    sender.credits = models.F("credits") - amount
    recipient.credits = models.F("credits") + amount
    sender.save(update_fields=["credits"])
    recipient.save(update_fields=["credits"])
```

## Views
- Use **Class-Based Views** for standard CRUD operations — they reduce boilerplate and are easily extended.
- Use **Function-Based Views** for simple, one-off endpoints or when CBV mixins make the code harder to follow.
- Use `get_object_or_404(Model, pk=pk)` instead of try/except `ObjectDoesNotExist` in views.
- Never put queryset logic directly in the view — delegate to the model manager or a service function.

## Django REST Framework (APIs)
- Use `ModelSerializer` for standard CRUD serializers; override only what differs.
- Use `ViewSet` + `Router` for full CRUD resources; `APIView` for custom endpoints.
- Always declare `permission_classes` and `authentication_classes` explicitly on every view — don't rely on global defaults alone.
- Validate all input with serializers at the API boundary. Never trust `request.data` directly.

```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.select_related("profile").filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.request.user.organization)
```

## Security
- Never store secrets in source code or `settings.py` — use environment variables via `django-environ` or `python-decouple`.
- Always set `ALLOWED_HOSTS`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE` in production settings.
- Use Django's built-in CSRF protection — never disable it for convenience.
- Avoid `raw()` and `extra()` queryset methods; if raw SQL is necessary, use parameterized queries only.

## Testing
- Use `pytest-django` with `@pytest.mark.django_db` rather than `unittest.TestCase`.
- Use **factories** (`factory_boy`) instead of fixtures for test data — they're more maintainable and composable.
- Test at three levels: unit (model methods, service functions), integration (view + DB), and API (serializer + endpoint with `APIClient`).
- Use `--reuse-db` in local development to speed up test runs; always create fresh DB in CI.

```python
import pytest
from rest_framework.test import APIClient

from tests.factories import UserFactory

@pytest.mark.django_db
def test_user_list_requires_auth():
    client = APIClient()
    response = client.get("/api/users/")
    assert response.status_code == 401

@pytest.mark.django_db
def test_user_list_returns_active_users():
    UserFactory.create_batch(3, is_active=True)
    UserFactory(is_active=False)
    client = APIClient()
    client.force_authenticate(user=UserFactory())
    response = client.get("/api/users/")
    assert response.status_code == 200
    assert len(response.data["results"]) == 3
```

## Signals
- Keep signal handlers thin — they should call a service function, not contain logic themselves.
- Register signals in an `AppConfig.ready()` method, not at module level.
- Avoid signals for anything you can accomplish with model `save()` overrides or `post_save` in a service — signals are harder to trace.
