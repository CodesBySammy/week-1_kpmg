# LAB-09: Production-Readiness Review & Limitations Audit

## 1. Objective
Conduct a formal Production-Readiness Review (PRR) and audit technical debt in the limitations register.

## 2. Prerequisites
Understanding of operational excellence, SRE practices, and release criteria.

## 3. Practical Task
Evaluate system gates against `PRODUCTION_READINESS_CHECKLIST.md` and verify evidence.

## 4. Step-by-Step Instructions
1. Open `docs/week5/production-readiness/PRODUCTION_READINESS_CHECKLIST.md`.
2. Validate that each gate references automated test results.
3. Audit `KNOWN_LIMITATIONS.md` for accuracy.
4. Compile final sign-off report.

## 5. Expected Result
Formal PRR sign-off approving Release Candidate `v1.0.0-rc1`.

## 6. Verification & Automated Validation
Review `docs/week5/production-readiness/FINAL_READINESS_REPORT.md`.

## 7. Challenge Questions
Why must a known limitations register never be sanitized or hidden before client handover?
