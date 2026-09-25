# Scope Change Request: SCR-2026-05

- **Request ID**: SCR-2026-05
- **Title**: Case Escalation Tiering & Multi-Department Segregation
- **Requested By**: Client Operations Committee (Global Corporate Services Inc.)
- **Date Submitted**: September 2026
- **Urgency / Priority**: High / Critical
- **Target Release**: Release Candidate 1 (v1.0.0-rc1)

---

## 1. Business Justification
GCSI operates three primary operational departments (Support, Billing, Legal). Recently, major enterprise clients experienced delays on mission-critical system outages because support cases lacked explicit SLA escalation categorization. 
Under the new client operating procedure:
1. Every case must have an explicit `escalation_tier`:
   - `STANDARD` (Default 48h resolution SLA)
   - `PRIORITY` (12h resolution SLA)
   - `CRITICAL_ESC` (2h urgent SLA)
2. Escalating an issue to `CRITICAL_ESC` is a consequential action that alters SLA tracking and notifies executive leadership; it requires an explicit approval token signed by an authorized `supervisor` or `admin`.
3. Cases must be labeled with their operating `department` (`SUPPORT`, `BILLING`, `LEGAL`) to enable departmental data segregation and prevent cross-department data leakage.

---

## 2. Detailed Technical Requirements
- **Data Model**: Extend `Case` model with `escalation_tier` (Enum) and `department` (String, default "SUPPORT").
- **API Contracts**: Update `CaseCreate`, `CaseUpdate`, `CaseResponse` schemas to support `escalation_tier` and `department`.
- **Tool Contracts**: Allow `update_ticket` tool to optionally update `escalation_tier` and `escalation_reason`.
- **Security / RBAC**: Enforce that only users with `supervisor` or `admin` roles can authorize transitions to `CRITICAL_ESC`. Provide application-level department isolation checks.
- **Backward Compatibility**: Existing database records and tests from Weeks 1–4 must continue to function without modification. All existing cases must cleanly default to `STANDARD` and `SUPPORT`.
