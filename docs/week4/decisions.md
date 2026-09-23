# Architecture Decision Records (ADRs)

## ADR-001: Explicit Finite State Machine for AI Workflows
- **Context:** Autonomous agents easily get trapped in infinite loops or hallucinate tool transitions.
- **Decision:** Implement a deterministic FSM with a validated state transition table (`VALID_TRANSITIONS`).
- **Consequences:** Predictable transitions, testable execution states, and deterministic fallback paths.

## ADR-002: Externalized Human Approval Token Manager
- **Context:** Consequential write actions require human verification.
- **Decision:** Human approval is managed via a dedicated, thread-safe token manager with TTL expiration and cryptographic verification.
- **Consequences:** The LLM cannot authorize itself; human oversight is enforced at the data layer.
