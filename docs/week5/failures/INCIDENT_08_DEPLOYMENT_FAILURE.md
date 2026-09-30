# Incident Report: INC-08 - Deployment & Configuration Failure

## 1. Symptom & Description
A container or server instance is booted with missing or invalid environment variables (e.g., missing `DATABASE_URL` or missing `JWT_SECRET_KEY`).

## 2. Expected Behavior
- Application startup lifecycle validates all required settings via Pydantic `BaseSettings`.
- Fails fast during startup with an informative configuration error message.
- Prevents container readiness probe from passing, blocking traffic routing.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_deployment_failure_missing_env_var`.

## 4. Root Cause Analysis
Lazy configuration loading causes runtime failures when the first user request accesses an unconfigured secret.

## 5. Remediation & Hardening
- Strict eager configuration validation at startup in `app/core/config.py`.
- Health check endpoints (`/health/live`, `/health/ready`) probe database connectivity and configuration integrity.
