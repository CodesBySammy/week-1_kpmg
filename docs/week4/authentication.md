# Authentication Architecture

## 1. Token-Based Authentication
Authentication is enforced using cryptographically signed HMAC-SHA256 bearer tokens (JSON Web Tokens):
- **Secret Key:** Injected via `JWT_SECRET` environment variable.
- **Claims:**
  - `sub`: User ID
  - `username`: Unique username
  - `role`: Role string (`viewer`, `agent`, `manager`, `admin`)
  - `exp`: Token expiration epoch timestamp (default 8 hours)

## 2. Token Issuance
Clients obtain tokens via `POST /api/v1/workflow/auth/token` with username, user ID, and role.
