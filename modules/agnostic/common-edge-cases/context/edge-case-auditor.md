# Skill: Edge Case Auditor

This skill helps the agent identify missing edge case handling in code, plans, or specifications. Use it to ensure that the "Day 0" experience and general application robustness are addressed.

## When to use
- Before finalizing a new feature plan.
- During code review of a new component or API endpoint.
- When the user asks for an "edge case audit".
- When building something from scratch ("Day 0").

## Procedure

1. **Review the Context:** Analyze the current file, plan, or target code.
2. **Identify Data Flows:** Determine where data is fetched, created, or modified.
3. **Check for "Day 0" Issues:**
   - What happens if the query returns an empty list?
   - Is there a placeholder or "Get Started" UI?
   - Are there null/undefined checks for new objects?
4. **Check for Robustness Issues:**
   - **Network:** Is there a loading state? What if the request fails?
   - **Validation:** Are there length limits? How are special characters handled?
   - **Concurrency:** Can this action be performed multiple times? Is there a race condition?
5. **Report Findings:** Provide a list of identified risks and specific recommendations for improvement.

## Example Audit Output

> ### Edge Case Audit: [Feature Name]
>
> **Identified Risks:**
> - **Empty State:** The `ProjectList` component doesn't handle the case where `projects` is an empty array.
> - **Input Validation:** The `projectName` input allows empty strings, which could lead to nameless projects.
> - **Race Condition:** Clicking "Save" multiple times triggers multiple API calls.
>
> **Recommendations:**
> - Add an `if (projects.length === 0)` check and render an `EmptyProjectState` component.
> - Add a `min-length` requirement and trim the `projectName` input.
> - Disable the "Save" button while the request is in flight.
