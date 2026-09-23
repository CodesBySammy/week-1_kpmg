# Week 4: Workflow Orchestration & Finite State Machine

## 1. State Machine Specification
The workflow implements a finite state machine with strict, valid state transitions.

```mermaid
stateDiagram-v2
    [*] --> REQUEST_RECEIVED
    REQUEST_RECEIVED --> INTENT_DETECTED: Route Query
    REQUEST_RECEIVED --> FAILED: Parse Error

    INTENT_DETECTED --> EXECUTING: Pure RAG Query
    INTENT_DETECTED --> TOOL_PROPOSED: Tool Needed
    INTENT_DETECTED --> FAILED: Invalid Query

    TOOL_PROPOSED --> EXECUTING: Safe Read (retrieve_case_details)
    TOOL_PROPOSED --> APPROVAL_REQUIRED: Consequential Write (update_ticket)
    TOOL_PROPOSED --> APPROVED: Pre-Approved Token Supplied
    TOOL_PROPOSED --> FAILED: Validation Error

    APPROVAL_REQUIRED --> APPROVED: Manager Approves
    APPROVAL_REQUIRED --> APPROVAL_REJECTED: Manager Rejects
    APPROVAL_REQUIRED --> APPROVAL_EXPIRED: TTL Exceeded (10 min)
    APPROVAL_REQUIRED --> FAILED: State Error

    APPROVED --> EXECUTING: Dispatch Tool
    APPROVED --> FAILED: Execution Error

    EXECUTING --> COMPLETED: Success
    EXECUTING --> TIMED_OUT: Timeout Exceeded (5.0s)
    EXECUTING --> FAILED: Unrecoverable Error

    COMPLETED --> [*]
    FAILED --> [*]
    APPROVAL_REJECTED --> [*]
    APPROVAL_EXPIRED --> [*]
```

## 2. State Validation & Context Model
State is tracked in `WorkflowContext` (defined in `workflow/state.py`) including:
- `request_id` (e.g. `req_abc123`)
- `correlation_id` (e.g. `corr_xyz789`)
- `username` and `user_role`
- `current_state` and `state_history` with transition timestamps and reasons
- `selected_tool` and `tool_arguments`
- `approval_id` and `approval_status`
- `tool_result` and `error`
