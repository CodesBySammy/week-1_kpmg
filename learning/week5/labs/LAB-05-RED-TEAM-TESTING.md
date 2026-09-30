# LAB-05: Red-Team Adversarial Penetration Testing

## 1. Objective
Simulate adversarial attacks against prompt injection guardrails, RBAC policies, and tool execution gates.

## 2. Prerequisites
Understanding of OWASP LLM Top 10 vulnerabilities.

## 3. Practical Task
Run red-team attack payloads against the API and verify that deterministic controls block 100% of attacks.

## 4. Step-by-Step Instructions
1. Inspect attack vectors in `docs/week5/security/ABUSE_CASES.md`.
2. Run `pytest tests/security/test_red_team_suite.py -v`.
3. Verify prompt injection string 'Ignore instructions' is rejected.
4. Verify cross-department case access returns HTTP 403.

## 5. Expected Result
16/16 red-team tests pass; zero unauthorized actions or prompt leaks.

## 6. Verification & Automated Validation
Run `pytest tests/security/test_red_team_suite.py`.

## 7. Challenge Questions
Can regex guardrails alone stop all prompt injections? What other defenses are required?
