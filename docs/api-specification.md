# REST API Technical Specification

## 1. Protocol & Service Overview
- **Base URL**: `http://127.0.0.1:8000`
- **API Versioning**: URL Path-based (`/api/v1`)
- **Protocol**: HTTP/1.1
- **Content-Type**: `application/json`
- **Interactive Documentation**:
  - Swagger UI: `http://127.0.0.1:8000/docs`
  - ReDoc: `http://127.0.0.1:8000/redoc`
  - Raw OpenAPI 3.1 Spec: [docs/openapi.json](file:///d:/week1_kpmg/case-management-backend/docs/openapi.json)

---

## 2. Global Error Contract
All failure responses (HTTP 4xx and 5xx) strictly follow this JSON envelope:

```json
{
  "error": {
    "code": "ERROR_CODE_STRING",
    "message": "Human-readable explanation of error",
    "details": null | [
      {
        "field": "body -> field_name",
        "message": "Specific validation failure message",
        "type": "error_type"
      }
    ]
  }
}
```

### Standard Error Codes:
- `CASE_NOT_FOUND` (404): The requested case ID does not exist.
- `USER_NOT_FOUND` (404): The referenced user ID does not exist.
- `REQUEST_VALIDATION_ERROR` (422): Input payload failed schema type or length bounds.
- `VALIDATION_ERROR` (422): Domain business invariant violation (e.g. attempting to update a closed case).
- `INTERNAL_ERROR` (500): Unexpected server failure (internal details masked from client).

---

## 3. Endpoints Specification

### 3.1 Health Check
Check operational vitality of the backend service.

- **Method & Path**: `GET /health`
- **Status Code**: `200 OK`
- **Response Example**:
  ```json
  {
    "status": "healthy",
    "app": "case-management-backend",
    "version": "1.0.0"
  }
  ```

---

### 3.2 Create Case
Create a new case in the system.

- **Method & Path**: `POST /api/v1/cases`
- **Success Status**: `201 Created`
- **Request Body (JSON)**:
  | Field | Type | Required | Constraints | Description |
  |---|---|---|---|---|
  | `title` | `string` | **Yes** | Min 1, Max 255 chars | Summary of the case |
  | `description` | `string` | No | Max 5000 chars | Detailed explanation |
  | `priority` | `string` | No | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` (Default: `MEDIUM`) | Priority tier |
  | `case_type` | `string` | No | `BUG`, `FEATURE_REQUEST`, `INQUIRY`, `COMPLAINT` (Default: `INQUIRY`) | Classification |
  | `created_by` | `integer` | **Yes** | `> 0` | ID of existing creator user |
  | `assigned_to`| `integer` | No | `> 0` | ID of existing assignee user |

- **Request Example**:
  ```json
  {
    "title": "Database connection pool exhausted",
    "description": "API latency spiked to 5000ms due to unreleased sessions.",
    "priority": "CRITICAL",
    "case_type": "BUG",
    "created_by": 1,
    "assigned_to": 2
  }
  ```

- **Response Example (`201 Created`)**:
  ```json
  {
    "id": 9,
    "title": "Database connection pool exhausted",
    "description": "API latency spiked to 5000ms due to unreleased sessions.",
    "status": "OPEN",
    "priority": "CRITICAL",
    "case_type": "BUG",
    "created_by": 1,
    "assigned_to": 2,
    "created_at": "2026-09-10T12:00:00Z",
    "updated_at": "2026-09-10T12:00:00Z",
    "resolved_at": null
  }
  ```

- **Error Responses**:
  - `404 Not Found`: Creator or assignee user ID does not exist (`USER_NOT_FOUND`).
  - `422 Unprocessable Entity`: Title is empty, created_by is negative, or invalid priority string.

---

### 3.3 Retrieve Case by ID
Fetch a single case by its unique identifier.

- **Method & Path**: `GET /api/v1/cases/{case_id}`
- **Path Parameters**:
  - `case_id` (`integer`, required): Unique ID of the case.
- **Success Status**: `200 OK`
- **Response Example (`200 OK`)**:
  ```json
  {
    "id": 1,
    "title": "Login page returns 500 error",
    "description": "Users clicking the login button see a 500 page.",
    "status": "OPEN",
    "priority": "CRITICAL",
    "case_type": "BUG",
    "created_by": 1,
    "assigned_to": 2,
    "created_at": "2026-09-03T12:00:00Z",
    "updated_at": "2026-09-03T12:00:00Z",
    "resolved_at": null
  }
  ```
- **Error Responses**:
  - `404 Not Found`: If `case_id` does not exist (`CASE_NOT_FOUND`).

---

### 3.4 Update Case
Update one or more attributes of an existing case.

- **Method & Path**: `PUT /api/v1/cases/{case_id}`
- **Path Parameters**:
  - `case_id` (`integer`, required): ID of the case to mutate.
- **Success Status**: `200 OK`
- **Request Body (JSON)**: All fields are optional. Only supplied fields are updated.
  ```json
  {
    "status": "RESOLVED",
    "priority": "HIGH",
    "assigned_to": 3
  }
  ```
- **Business Rules**:
  1. If `status` transitions to `RESOLVED`, `resolved_at` is automatically stamped with the current UTC timestamp.
  2. If the case currently has `status == 'CLOSED'`, any attempt to modify `status` is rejected.
  3. Every changed attribute is automatically recorded in the `case_history` audit table.
- **Response Example (`200 OK`)**:
  ```json
  {
    "id": 1,
    "title": "Login page returns 500 error",
    "description": "Users clicking the login button see a 500 page.",
    "status": "RESOLVED",
    "priority": "HIGH",
    "case_type": "BUG",
    "created_by": 1,
    "assigned_to": 3,
    "created_at": "2026-09-03T12:00:00Z",
    "updated_at": "2026-09-10T12:00:00Z",
    "resolved_at": "2026-09-10T12:00:00Z"
  }
  ```

---

### 3.5 List Cases (with Pagination & Filtering)
Retrieve a paginated collection of cases with optional query filters.

- **Method & Path**: `GET /api/v1/cases`
- **Query Parameters**:
  | Parameter | Type | Default | Constraints | Description |
  |---|---|---|---|---|
  | `skip` | `integer` | `0` | `>= 0` | Offset for pagination |
  | `limit` | `integer` | `100` | `1 <= limit <= 500` | Maximum cases returned |
  | `status` | `string` | `None` | `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` | Filter by status |
  | `priority`| `string` | `None` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` | Filter by priority |

- **Response Example (`200 OK`)**:
  ```json
  {
    "cases": [
      {
        "id": 1,
        "title": "Login page returns 500 error",
        "status": "OPEN",
        "priority": "CRITICAL",
        "case_type": "BUG",
        "created_by": 1,
        "assigned_to": 2,
        "created_at": "2026-09-03T12:00:00Z",
        "updated_at": "2026-09-03T12:00:00Z",
        "resolved_at": null
      }
    ],
    "total": 1
  }
  ```

---

### 3.6 Create User & List Users
Supporting endpoints to register users and view team members.

- **Create User**: `POST /api/v1/users` (Returns `201 Created`)
  ```json
  {
    "username": "sgupta",
    "email": "sgupta@example.com",
    "full_name": "Siddharth Gupta",
    "role": "analyst"
  }
  ```
- **List Users**: `GET /api/v1/users` (Returns `200 OK` with array of users).
