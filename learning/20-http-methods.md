# Module 20: HTTP Methods, Idempotency & Safety Guarantees

## 1. What It Is
**HTTP Methods** (also called HTTP Verbs) indicate the desired action to be performed on the identified resource. The HTTP/1.1 specification (RFC 7231 / RFC 9110) formally defines standardized semantics for methods including `GET`, `POST`, `PUT`, `PATCH`, and `DELETE`.

## 2. Why It Exists
HTTP is not just a transport protocol; it is an application protocol with built-in semantics. By adhering to standard methods, intermediaries (browsers, content delivery networks, proxies, caches, and API gateways) understand how to handle requests automatically: whether they can cache the response, retry upon a network failure, or prefetch links safely.

## 3. The Core Properties: Safety and Idempotency

```mermaid
graph TD
    subgraph Safe Operations: Never Mutates State
        GET[GET: Read-only]
        HEAD[HEAD: Headers only]
    end
    
    subgraph Idempotent Mutations: Multiple Identical Calls = Same Result
        PUT[PUT: Replace entire resource]
        DELETE[DELETE: Remove resource]
    end
    
    subgraph Non-Idempotent Mutations: Multiple Calls = Multiple Side Effects
        POST[POST: Create new resource / append]
    end
```

### 1. Safe Methods
An HTTP method is **safe** if calling it does not alter the server's resource state. Safe methods are strictly read-only.
- `GET`, `HEAD`, `OPTIONS` are safe.
- Calling `GET /api/v1/cases/42` one million times has zero effect on the database.

### 2. Idempotent Methods
An HTTP method is **idempotent** if the side-effect of making $N > 0$ identical requests is the same as making a single request.
- `PUT`, `DELETE`, `GET`, `HEAD` are idempotent.
- If a network glitch drops a response from `PUT /cases/42`, the client can safely retry the exact same request without corrupting or duplicating state.
- **`POST` is NOT idempotent**: Sending `POST /cases` five times creates five duplicate tickets!

## 4. Method Semantic Matrix

| HTTP Method | Purpose | Request Body? | Response Body? | Safe? | Idempotent? | Success Status Code |
|---|---|---|---|---|---|---|
| **GET** | Retrieve a resource representation | No | Yes | **Yes** | **Yes** | 200 OK |
| **POST** | Create a new resource or execute processing | **Yes** | Yes | No | **No** | 201 Created |
| **PUT** | Replace a resource or update state | **Yes** | Yes | No | **Yes** | 200 OK / 204 No Content |
| **PATCH** | Apply partial modifications to a resource | **Yes** | Yes | No | No / Conditional | 200 OK |
| **DELETE** | Remove a resource | Optional | Optional | No | **Yes** | 200 OK / 204 No Content |

## 5. PUT vs. PATCH: Architectural Distinction
- **`PUT` (Complete Replacement / Upsert)**:
  The client sends the *entire* representation of the resource. Any field omitted by the client is reset to its default or `NULL`.
- **`PATCH` (Partial Modification)**:
  The client sends only the specific attributes it wishes to mutate. Omitted fields remain completely untouched.

*Implementation Note*: In our project's `PUT /api/v1/cases/{case_id}`, we implement partial updating using Pydantic's `exclude_unset=True` pattern, which is the most common pragmatic REST pattern used in modern web APIs.

## 6. Where Data Travels in HTTP Requests
In FastAPI, you control where parameters originate using type hints and parameter functions:

### 1. Path Parameters: Identifying the Resource
```python
@router.get("/cases/{case_id}")
def get_case(case_id: int): # Extracted from URL path /cases/101
```

### 2. Query Parameters: Filtering, Sorting, and Pagination
```python
@router.get("/cases")
def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[CaseStatus] = Query(None), # From /cases?status=OPEN&limit=10
):
```

### 3. Request Body: Payload Data (JSON)
```python
@router.post("/cases", status_code=201)
def create_case(case_data: CaseCreate): # Deserialized from HTTP Request Body
```

## 7. Common Mistakes
1. **Returning 200 OK on Resource Creation**:
   - `POST /cases` should return **201 Created**, not 200 OK!
2. **Accepting JSON Body in a GET Request**:
   - Although technically possible in HTTP/1.1, many proxies and CDN caches strip GET bodies. Always pass search/filter criteria in query parameters for GET requests.
3. **Failing to make PUT idempotent**:
   - If a PUT endpoint increments a counter (`hits = hits + 1`), it is NOT idempotent and violates the HTTP specification.

## 8. Practical Exercises
1. Open [app/api/routes/cases.py](file:///d:/week1_kpmg/case-management-backend/app/api/routes/cases.py). Locate where `status_code=201` is declared on `POST /cases`. Why is 201 used instead of the default 200?
2. Execute a `PUT /cases/{id}` request using the FastAPI interactive documentation (`/docs`) updating only the `priority` field. Verify that other fields (like `title` and `description`) remain intact.

## 9. Interview Questions & Model Answers
**Q: What is the difference between an Idempotent HTTP method and a Safe HTTP method?**
*Answer:* A safe method (like `GET` or `HEAD`) is strictly read-only and causes no state changes on the server. An idempotent method (like `PUT` or `DELETE`) modifies server state, but executing it multiple times with the same payload results in the exact same server state as executing it once. Thus, all safe methods are idempotent, but not all idempotent methods are safe.

## 10. Short Self-Test
1. Which HTTP method is specifically intended to be non-idempotent for creating resources? *(Answer: `POST`).*
2. If you want to filter cases by status `?status=OPEN`, which part of the HTTP request should carry this parameter? *(Answer: The Query String / Query Parameters).*
