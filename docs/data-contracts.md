# Enterprise Data Contracts Specification: Case Management Platform

## 1. Executive Summary

A **Data Contract** is a formal, version-controlled agreement between data producers (the Case Management transactional service) and data consumers (analytical pipelines, business intelligence dashboards, compliance auditors, and AI models).

This document formalizes the Data Contracts governing the Case Management Data Platform, specifying schema structure, nullability, allowable domains, semantic constraints, and schema evolution rules.

---

## 2. Ingestion Contracts (Source Interfaces)

### Contract 1: Operational Cases Ingestion Contract (`cases_source_contract`)
* **Target Dataset**: `cases`
* **Version**: `1.0.0`
* **Producer**: Case Management Transactional Service (CSV Export / CDC Feed)
* **Consumer**: Case Management Data Pipeline (Raw & Standardized Layers)
* **Owner**: Backend Core Team

#### Column Specifications:
| Column Name | Ingestion Type | Nullable? | Primary Key? | Semantic Rules / Allowed Domain |
|---|:---:|:---:|:---:|---|
| `case_id` | `string` $\rightarrow$ `Int64` | **NO** | **YES** | Natural key; must coerce to integer $> 0$. |
| `title` | `string` | **NO** | NO | Length $3 \le \text{len} \le 200$; whitespace trimmed. |
| `description` | `string` | YES | NO | Nulls imputed to `"No description provided"`. |
| `status` | `string` | **NO** | NO | Allowed enum: `['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']`. |
| `priority` | `string` | **NO** | NO | Allowed enum: `['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']`. |
| `case_type` | `string` | **NO** | NO | Allowed enum: `['BUG', 'FEATURE_REQUEST', 'INQUIRY', 'COMPLAINT']`. |
| `created_by` | `string` $\rightarrow$ `Int64` | **NO** | NO | Must resolve to valid `user_id` in reference lookup. |
| `assigned_to` | `string` $\rightarrow$ `Int64` | YES | NO | If present, must resolve to valid `user_id` in reference lookup. |
| `created_at` | `string` $\rightarrow$ `UTC timestamp` | **NO** | NO | Must be parseable ISO-8601 UTC timestamp. |
| `updated_at` | `string` $\rightarrow$ `UTC timestamp` | **NO** | NO | Must be $\ge \text{created\_at}$. |
| `resolved_at` | `string` $\rightarrow$ `UTC timestamp` | YES | NO | If populated, must be $\ge \text{created\_at}$. |

---

### Contract 2: Reference Users Contract (`reference_users_contract`)
* **Target Dataset**: `reference_users`
* **Version**: `1.0.0`
* **Producer**: HR / Active Directory Sync (`reference.json`)

| Column Name | Target Type | Nullable? | Primary Key? | Allowed Domain |
|---|:---:|:---:|:---:|---|
| `user_id` | `int64` | **NO** | **YES** | Positive integer $> 0$. |
| `username` | `string` | **NO** | NO | Alphanumeric lowercased string. |
| `department_id` | `string` | **NO** | NO | Resolves to `departments` reference key. |
| `tier` | `string` | **NO** | NO | Allowed enum: `['L1', 'L2', 'L3']`. |
| `region` | `string` | **NO** | NO | Allowed enum: `['EMEA', 'APAC', 'AMER']`. |

---

### Contract 3: Compliance & SLA Policies Contract (`policy_metadata_contract`)
* **Target Dataset**: `policies`
* **Version**: `1.0.0`
* **Producer**: Governance Engine (`policy_metadata.parquet` / REST API)

| Column Name | Target Type | Nullable? | Primary Key? | Allowed Domain |
|---|:---:|:---:|:---:|---|
| `policy_id` | `string` | **NO** | **YES** | Unique policy code (e.g. `POL-SEC-01`). |
| `case_type` | `string` | **NO** | NO | Composite join key with `priority`. |
| `priority` | `string` | **NO** | NO | Composite join key with `case_type`. |
| `sla_target_hours` | `float64` | **NO** | NO | SLA threshold (e.g. `2.0`, `4.0`, `24.0`, `72.0`). |
| `compliance_framework` | `string` | **NO** | NO | Regulatory body (e.g. `ISO27001`, `GDPR`, `SOC2`). |

---

## 3. Schema Evolution Policies

To prevent unnecessary pipeline breakage while defending downstream integrity:
1. **Additive Changes (Non-Breaking)**: Upstream producers may introduce new optional columns (e.g. `tags`, `customer_sentiment`) at any time. The ingestion engine tolerates unknown columns, landing them into Bronze raw Parquet without crashing.
2. **Subtractive / Renaming Changes (Breaking)**: Deleting or renaming a declared required column (`case_id`, `title`, `status`) constitutes a contract breach. Producers must notify consumers and increment the major contract version (`v2.0.0`).
3. **Enum Expansion**: Introducing a new categorical status (e.g. `'TRIAGED'`) requires prior contract approval and deployment of updated quality rules. Unapproved enums are safely quarantined.

---

## 4. Enforcement Engine Architecture

Contracts are defined in `pipeline/schemas/contracts.py` as typed dataclasses. The `SchemaValidator` executes contract checks during Stage 4 of pipeline orchestration. Violations are formatted with exact failure counts, offending column names, and sample values, which are attached directly to execution manifests and quarantine alerts.
