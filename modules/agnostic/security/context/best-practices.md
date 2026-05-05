# API Security: Best Practices

## Zero Public Exposure
- **Auth by Default:** All endpoints should require authentication by default. Use an allow-list for the few truly public endpoints (e.g., login, documentation, health-check).
- **No Naked Endpoints:** Never expose backend endpoints without a secondary layer of protection (e.g., API Gateway, WAF, or Reverse Proxy).
- **Internal APIs:** Ensure internal/management APIs are isolated on private networks and not reachable from the public internet.

## Rate Limiting & Throttling
- **Graceful Throttling:** Implement rate limits at multiple levels (IP-based, User-based, and Global).
- **Informative Responses:** Return `429 Too Many Requests` with a `Retry-After` header. Provide clear feedback to the client rather than just dropping the connection.
- **Circuit Breakers:** Implement circuit breakers for downstream services to prevent cascading failures during traffic spikes or outages.

## Data Integrity & Validation
- **Input Validation:** Treat all external input as malicious. Use strict schemas (e.g., Pydantic, Zod, JSON Schema) to validate request bodies, query params, and headers.
- **Sanitization:** Sanitize data before using it in database queries (SQLi protection), shell commands, or HTML rendering (XSS protection).
- **Encryption:** Use TLS 1.2+ for all data in transit. Encrypt sensitive data at rest using strong cryptographic standards (e.g., AES-256).

## Observability & Defense
- **Audit Logging:** Log all security-significant events (login attempts, permission changes, rate-limit hits) with relevant context (user ID, IP, timestamp).
- **Security Headers:** Enforce security headers like `Content-Security-Policy`, `X-Frame-Options`, and `Strict-Transport-Security`.
- **Fail Securely:** Ensure that if a security check fails, the application defaults to a "deny" state rather than continuing with partial permissions.
