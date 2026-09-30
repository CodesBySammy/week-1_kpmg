# Enterprise Rollback Procedure & Disaster Recovery

## 1. Rollback Triggers
- Elevated HTTP 5xx error rate (> 1.0%) for 5 consecutive minutes post-deployment.
- Failure of Kubernetes readiness probes to pass within 5 minutes.
- Unhandled data corruption detected in bronze/silver lakehouse ingestion.

## 2. Step-by-Step Rollback Execution

### Kubernetes Workload Rollback:
```bash
# Roll back deployment to previous revision
kubectl rollout undo deployment/case-management-backend -n production

# Verify rollback status
kubectl rollout status deployment/case-management-backend -n production
```

### Database Schema Downgrade:
If the failed deployment included database migrations that altered schema:
```bash
# Downgrade schema one revision
alembic downgrade -1
```

## 3. Post-Rollback Validation
1. Execute `/health/ready` probe.
2. Run regression smoke test suite (`pytest tests/regression/test_regression_suite.py`).
3. Notify SRE on-call lead and file incident post-mortem.
