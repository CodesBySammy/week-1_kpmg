# CI/CD Pipeline & Automated Release Gates

## 1. Pipeline Stages (.github/workflows/ci.yml)
1. **Lint & Style Check:** Flake8 and formatting validation.
2. **Test Suite Execution:** Pytest execution across all 143 unit and integration tests.
3. **Coverage Gate:** Automated failure if total test coverage falls below 70.0%.
4. **Security Scan:** Verification of prompt injection tests and authorization barriers.
5. **Container Build:** Docker image build validation.
