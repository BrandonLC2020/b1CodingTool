# Application Robustness: Common Edge Cases

Beyond the first launch, applications must be resilient to environmental factors and unexpected user behavior.

## Network Interruptions & Partial Data
In a distributed system, network failures are inevitable. Applications should handle these gracefully.

- **Retry Logic:** Implement exponential backoff for transient failures (e.g., 503 Service Unavailable).
- **Offline States:** If the network is down, inform the user and disable features that require a connection.
- **Optimistic UI:** Show the result of an action immediately (assuming success) and roll back if the actual request fails.
- **Loading States:** Provide visual feedback while data is in flight.

## Input Validation & Sanitization
Assume all user-supplied input is potentially malformed or malicious.

- **Boundary Testing:** Handle extremely long strings, empty strings, and negative numbers.
- **Character Sets:** Support Unicode/Emojis and sanitize inputs to prevent injection attacks (SQLi, XSS).
- **Type Safety:** Ensure that "1" (string) and 1 (integer) are handled correctly based on the expected type.
- **Null/Undefined:** Always check if a value exists before accessing its properties.

## Concurrency & Race Conditions
When multiple agents, users, or background processes interact with the same state, race conditions can occur.

- **Atomic Operations:** Use database transactions or atomic state updates to ensure consistency.
- **Optimistic Locking:** Use versioning or timestamps to detect if a record has changed since it was last read.
- **Idempotency:** Ensure that repeating the same action multiple times (e.g., clicking a "Submit" button twice) has the same effect as a single action.
- **Visibility:** Inform the user if a resource they are editing has been modified by someone else.

## Error Handling
Errors should be a source of information, not just frustration.

- **Human-Readable Messages:** "An error occurred" is unhelpful. Use "Failed to save project due to a network timeout. Please try again."
- **Actionable Advice:** If possible, tell the user how to fix the problem (e.g., "Check your internet connection").
- **Graceful Degradation:** If a non-critical feature fails, allow the rest of the application to continue functioning.
