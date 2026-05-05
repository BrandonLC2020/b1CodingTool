# API Security: Conventions

## Error Responses
Always use standardized HTTP status codes for security events:
| Code | Meaning | Context |
|------|---------|---------|
| `401` | Unauthorized | Missing or invalid authentication token. |
| `403` | Forbidden | Authenticated but lacking necessary permissions. |
| `429` | Too Many Requests | Rate limit exceeded. |
| `503` | Service Unavailable | Circuit breaker is open. |

## Header Standards
Required security headers for production APIs:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy: default-src 'none'; ...`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## Naming & Access
- Use `/api/v1/private/...` for internal/admin routes.
- Use `/api/v1/public/...` only for explicitly reviewed public endpoints.
- Environment variables for security settings should follow the `SEC_...` prefix (e.g., `SEC_API_KEY_ROTATION_DAYS`).
