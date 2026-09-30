# Release Candidate Deployment Validation Script

## Automated Smoke Verification Workflow

Run the following test sequence to validate a newly deployed instance:

```bash
# 1. Probe health endpoints
curl -f http://localhost:8000/health/live
curl -f http://localhost:8000/health/ready

# 2. Authenticate as investigator
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "investigator_user", "password": "secure_password"}' | jq -r .access_token)

# 3. Retrieve existing case
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/cases/ | jq .

# 4. Perform Grounded RAG query
curl -s -X POST http://localhost:8000/api/v1/rag/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the policy for priority escalations?"}' | jq .
```
