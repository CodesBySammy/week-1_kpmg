# Current-State System Analysis

## 1. Request Processing Lifecycle
1. **Entry**: Client issues HTTP request to FastAPI application.
2. **Security & Context**: Middleware extracts or injects X-Correlation-ID, sets request context for structured logging.
3. **Authentication**: JWT token validated in Authorization header; claims decoded to extract user ID, username, and role.
4. **Guardrails**: Input payload scanned for control characters, length constraints, and prompt injection patterns.
5. **Routing & Execution**:
   - If user asks a policy question -> Routed to RAG pipeline.
   - If user requests case inspection -> Routed to 
etrieve_case tool.
   - If user requests ticket modification -> Routed to update_ticket tool; if consequential, state machine halts and requests human approval token.
6. **Audit & Response**: Entity mutation logged to AuditLog; response returned with latency metadata and correlation ID.

## 2. Component Health
- All 143 baseline tests passing.
- Test coverage across core modules: 90.63%.
- CI/CD pipeline enforces formatting, linting, unit tests, and coverage thresholds.
