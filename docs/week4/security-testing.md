# Security Testing & Failure Exercises

## 1. Security Test Cases Verified
1. **Unauthenticated Request:** Calling `/execute` without Bearer token returns 401 Unauthorized.
2. **Unauthorized Role:** Attempting manager actions with agent role returns 403 Forbidden.
3. **Bypass Approval:** Calling `update_ticket` without approval token raises `APPROVAL_REQUIRED`.
4. **Forged Approval Token:** Non-existent or forged token raises `INVALID_APPROVAL`.
5. **Expired Token:** Approval used after TTL expiration raises expiration error.
6. **Prompt Injection:** Malicious inputs attempting instruction override are sanitized and detected.
