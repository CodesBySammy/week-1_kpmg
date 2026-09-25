# Automated Case Management Policy Audits

## 1. Integration with Case Management
The platform links case records with corporate policy knowledge:
- `POST /api/v1/rag/cases/{case_id}/policy-check`
- Retrieves case details (title, description, status) from SQLite.
- Formulates compliance questions and searches the corporate policy knowledge base.
- Generates policy compliance guidance citing specific clauses.
