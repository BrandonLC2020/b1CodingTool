# Day 0: The First Launch Experience

The "Day 0" experience refers to the state of an application when it is first launched by a user, before any data has been created or persisted. Handling this gracefully is critical for user onboarding and preventing "empty screen" syndrome.

## Empty Tables & Missing Objects
When a query returns no results (e.g., a new user with no "Projects" or "Tasks"), the application should never display a raw error or a completely blank container.

### Patterns for Success
- **Placeholder UI:** Show a friendly "No [Items] yet!" message.
- **Get Started UI:** Provide a clear "Call to Action" (CTA) to help the user create their first object (e.g., a "Create Task" button).
- **Onboarding Content:** Pre-populate the app with "Welcome" or "Sample" data that the user can interact with or delete.
- **Illustration/Empty States:** Use a visual aid to make the empty state feel intentional and polished.

### Anti-Patterns to Avoid
- **Blank Screens:** Users may think the app is broken or still loading.
- **Raw Null/Undefined Errors:** "Cannot read property 'map' of undefined" is a common failure when data is expected but missing.
- **Generic Loading Spinners:** Don't keep a spinner active forever if the data is successfully fetched but is simply empty.

## Initial Setup
If the application requires initial configuration (e.g., API keys, Workspace selection), guide the user through this process immediately.

- **Setup Wizards:** Use a step-by-step flow for mandatory configuration.
- **Validation:** Confirm that the initial setup is successful before allowing the user into the main app.
- **Fallback States:** If a required service is unavailable, explain the situation clearly and provide alternatives.
