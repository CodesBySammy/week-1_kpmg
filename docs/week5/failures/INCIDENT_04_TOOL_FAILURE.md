# Incident Report: INC-04 - Agentic Tool Execution Failure

## 1. Symptom & Description
An agentic tool invocation (`update_ticket` or `retrieve_case`) targets a non-existent case identifier (e.g., `CASE-99999`) or database connection encounters a transient lock.

## 2. Expected Behavior
- The tool contract must catch domain exceptions.
- Return a typed `ToolError(error_code="CASE_NOT_FOUND", message="...")` rather than throwing an unhandled exception.
- The workflow orchestrator captures the tool error, transitions state to `FAILED` or returns a controlled message to the user, recording an audit entry.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_tool_failure_invalid_ticket_id`.

## 4. Root Cause Analysis
Direct database queries inside tool functions without structured exception encapsulation previously threatened to crash the async event loop.

## 5. Remediation & Hardening
- Wrapped all tool executions with Pydantic tool result/error envelopes (`ToolOutput`, `ToolError`).
- Added structured audit event `TOOL_EXECUTION_FAILED` with tool name, caller identity, and error message.
