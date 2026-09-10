# Module 25: Engineering Documentation & Architecture Decision Records (ADRs)

## 1. What It Is
**Engineering Documentation** is the set of technical specifications, architecture blueprints, setup runbooks, and decision logs that explain how a software system is designed, installed, operated, tested, and maintained. It is an equal deliverable to the source code itself.

## 2. Why It Exists
Undocumented or poorly documented software is unusable software:
- **The "Tribal Knowledge" Trap**: When key design decisions exist only inside a senior engineer's head, the team is paralyzed when that engineer is sick or leaves the company.
- **Onboarding Friction**: New engineers take weeks to set up local environments because undocumented prerequisites and environment variables fail silently.
- **Lost Rationale (Chesterton's Fence)**: Years later, an engineer sees an unusual line of code, doesn't know why it was written, deletes it, and reintroduces a subtle production outage.

## 3. Why Backend Engineers Use It
- **Reproducibility**: Enables any engineer to clone the repository and run the full service and test suite within 5 minutes on a clean machine.
- **Compliance & Audit Readiness**: Enterprise SOC 2 and ISO audits mandate formal architecture documentation, data flow diagrams, and security specifications.
- **Defensible Design**: Architecture Decision Records (ADRs) document why a technology or pattern was selected over alternatives, preventing circular arguments in future team meetings.

## 4. The Anatomy of a World-Class Technical README
A professional backend `README.md` must contain:
1. **Header & System Overview**: What problem does this service solve?
2. **Architecture Summary & Diagram**: Visual map of layers, dependencies, and protocols.
3. **Prerequisites**: Exact runtime versions (Python 3.10+, Git 2.30+).
4. **Step-by-Step Setup Runbook**: Copy-pasteable shell commands from `git clone` to running server.
5. **Database Initialization & Seeding**: How to run migrations or seed scripts.
6. **Testing & Coverage Commands**: Exact commands to verify the build.
7. **Interactive API Documentation Links**: Where to find Swagger UI and ReDoc.
8. **Configuration Reference**: Table of every supported environment variable.
9. **Troubleshooting Guide**: Known failure modes, error messages, and immediate fixes.

## 5. Architecture Decision Records (ADRs): The Industry Standard
Whenever an engineering team makes a significant architectural choice, they record it in an ADR using this standard format:

### Standard ADR Template:
- **Title**: Context and Decision (e.g. `ADR-001: SQLite vs. PostgreSQL for Week 1`)
- **Status**: Proposed / Accepted / Superseded
- **Context**: The problem statement and environmental constraints.
- **Decision**: The chosen path.
- **Alternatives Considered**: Why option B and C were rejected.
- **Trade-offs & Consequences**: Both positive benefits and negative limitations introduced.

See our project's [docs/decisions.md](file:///d:/week1_kpmg/case-management-backend/docs/decisions.md) for live examples of this pattern!

## 6. Living Documentation vs. Documentation Rot
To prevent documentation from becoming obsolete ("rot"):
- **Automate whatever can be automated**: Do not manually document JSON payloads; generate them automatically via OpenAPI (`/docs` and `docs/openapi.json`).
- **Treat Docs as Code**: Keep documentation in the same repository as the code (`docs/` folder). A pull request modifying business logic must include corresponding doc updates.
- **Test Setup from Scratch**: Regularly test setup instructions on a fresh machine or container to catch missing steps.

## 7. Common Mistakes
1. **Assuming "Tribal Knowledge"**: Writing "install dependencies" without specifying `pip install -e .` or the exact virtualenv commands.
2. **Hardcoding localhost passwords in docs**: Encourages bad security practices.
3. **Stale Diagrams**: Architecture diagrams that show services or databases that were deprecated six months ago.

## 8. Practical Exercises
1. Inspect the documentation suite in `docs/` (`architecture.md`, `database-design.md`, `decisions.md`, `api-specification.md`). Identify the 4 architectural alternatives evaluated in `decisions.md`.
2. Follow the setup runbook in [README.md](file:///d:/week1_kpmg/case-management-backend/README.md) as if you were a brand-new engineer who just joined the team.

## 9. Interview Questions & Model Answers
**Q: What is an Architecture Decision Record (ADR), and why is it valuable to an engineering organization?**
*Answer:* An Architecture Decision Record (ADR) is a short, version-controlled document that captures a significant architectural choice along with its context, alternatives considered, rationale, and consequences/trade-offs. ADRs prevent "decision amnesia," provide historical context for why the system is built a certain way, and prevent new team members from re-litigating settled design choices without understanding the historical constraints.

## 10. Short Self-Test
1. What does ADR stand for in software engineering? *(Answer: Architecture Decision Record).*
2. Where should technical documentation live to prevent it from drifting out of sync with application code? *(Answer: In the same version-controlled Git repository as the source code).*
