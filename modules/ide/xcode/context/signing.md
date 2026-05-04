# Xcode: Signing & Identity

## Development Signing
- **Automatic Signing:** Use Xcode's automatic signing for local development.
- **Config:** Specify the `DEVELOPMENT_TEAM` and `ORGANIZATION_NAME` in the `Settings` block of `Project.swift`.

## Configuration Management
- **Bundle IDs:** Define a `bundleIdPrefix` (e.g., `com.mycompany`) and derive target bundle IDs programmatically in the manifest.
- **Entitlements:** Store `.entitlements` files in the target's folder and link them explicitly in `Project.swift`.

## Security
- Never commit distribution certificates or provisioning profiles to the repository.
- Use environment variables or secure vault storage for CI/CD signing identities.
