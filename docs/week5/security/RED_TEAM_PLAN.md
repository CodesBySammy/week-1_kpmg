# Week 5 Red-Team Penetration Testing Plan

## Objective
Subject the integrated Weeks 1–5 platform to systematic adversarial attacks covering the four required curriculum vectors:
1. Prompt Injection & Jailbreaking
2. Access Leakage & Privilege Escalation
3. Malformed Data Injection
4. Unsafe Tool Requests

## Methodology
- Automated test execution via `tests/security/test_red_team_suite.py` (16 test cases).
- Zero reliance on LLM self-policing; verification that deterministic application code blocks every attack.
- Verification that all attempted breaches produce security audit records.

## Schedule & Environment
- Environment: Local isolated test runner, Python 3.14.7.
- Tools: Pytest, HTTPX TestClient, Mock LLM Provider with injection payload fixtures.
