# Role-Based Access Control (RBAC)

## 1. Permission Matrix
| Role | READ_CASE | EXECUTE_TICKET_UPDATE | APPROVE_TICKET | QUERY_POLICY_RAG | ADMIN_OPS |
|---|:---:|:---:|:---:|:---:|:---:|
| **viewer** | | | | x | |
| **agent** | x | x (requires approval) | | x | |
| **manager**| x | x | x | x | |
| **admin**  | x | x | x | x | x |

## 2. Enforcement Points
Permissions are checked deterministically in code via `security.rbac.check_permission(...)`:
- At API endpoint route handlers using FastAPI dependencies.
- Inside tool execution functions before any database access or mutation occurs.
