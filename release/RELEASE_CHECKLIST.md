# Pre-Release & Deployment Checklist (v1.0.0-rc1)

## Stage 1: Code & Testing Integrity
- [x] All 221 automated tests passing (`pytest tests/`).
- [x] Zero regressions against Weeks 1–4 baselines.
- [x] Zero hardcoded passwords, API keys, or secrets in git history.
- [x] Linter and type checks clean.

## Stage 2: Packaging & Deployment
- [x] Dockerfile builds cleanly without root vulnerabilities.
- [x] Environment variables documented in `.env.example`.
- [x] Database migration scripts verified with rollback tested.
- [x] Liveness (`/health/live`) and readiness (`/health/ready`) probes operational.

## Stage 3: Operational Handover
- [x] Support Runbook published (`docs/week5/operations/SUPPORT_RUNBOOK.md`).
- [x] Troubleshooting Catalog available (`docs/week5/failures/FAILURE_CATALOG.md`).
- [x] Ownership Matrix defined (`docs/week5/handover/OWNERSHIP_MATRIX.md`).
- [x] Demo scripts and stakeholder slide notes verified (`docs/week5/demo/`).
