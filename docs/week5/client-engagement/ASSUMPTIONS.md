# Technical Assumptions Register

1. **Network Independence**: The test suite and core workflows must execute fully offline without mandatory internet connectivity.
2. **Local Identity Issuance**: Development environment uses local HMAC-SHA256 JWT generation with configured shared secret.
3. **Storage Persistence**: File system directories data/, udit/, and 
eports/ are writable by the application process.
4. **Approval Authority**: Only tokens signed with the authoritative approval secret and carrying the supervisor or dmin role are valid for consequential execution.
