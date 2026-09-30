# LAB-01: Technical Discovery & Stakeholder Interview Simulation

## 1. Objective
Perform structured technical discovery on a legacy case management workflow and map pain points into technical requirements.

## 2. Prerequisites
Python 3.14+ environment, access to `docs/week5/client-engagement/`.

## 3. Practical Task
Inspect legacy CSV data feeds and interview simulated stakeholders to identify schema inconsistencies and compliance retention mandates.

## 4. Step-by-Step Instructions
1. Read `CLIENT_PROCESS_BRIEF.md`.
2. Review legacy case data in `pipeline/sources/`.
3. Run data profiler `python -m pipeline.profiler`.
4. Document discovered constraints in `CONSTRAINTS.md`.

## 5. Expected Result
Structured inventory of legacy data columns, data quality failure rates, and non-functional requirements.

## 6. Verification & Automated Validation
Check that `docs/week5/client-engagement/TECHNICAL_DISCOVERY.md` reflects discovered schema issues.

## 7. Challenge Questions
What discovery question would you ask if a client claims their data 'never has null values'?
