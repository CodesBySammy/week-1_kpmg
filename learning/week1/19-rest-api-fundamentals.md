# Module 19: REST API Fundamentals & Resource Modeling

## 1. What It Is
**REST (Representational State Transfer)** is an architectural style for distributed hypermedia systems, formulated by Roy Fielding in his 2000 doctoral dissertation. A RESTful API exposes server-side entities as **resources** identified by unique URIs, which clients manipulate using standard, universal HTTP operations.

## 2. Why It Exists
Before REST, remote communication relied on complex, tightly coupled protocols like SOAP, XML-RPC, and CORBA:
- They required specialized client libraries and bloated XML envelopes.
- They treated the network like remote function calls (RPC), inventing arbitrary action verbs: `/doCreateCase`, `/fetchCaseById`, `/updateCaseStatus`.
- They ignored the native power of the HTTP protocol (caching, status codes, headers, methods).

REST simplified distributed systems by using HTTP itself as the application protocol.

## 3. The 6 Guiding Constraints of REST
To be truly RESTful, an architecture must satisfy six core constraints:

```mermaid
graph TD
    CS[1. Client-Server<br>UI concerns separated from data storage]
    SL[2. Stateless<br>Each request contains all information needed to process it]
    CA[3. Cacheable<br>Responses explicitly define their cacheability]
    UI[4. Uniform Interface<br>Standard resource URIs and self-descriptive messages]
    LS[5. Layered System<br>Client cannot tell whether it is connected directly to server or proxy]
    COD[6. Code-on-Demand (Optional)<br>Server can extend client functionality by transferring scripts]
```

### The Cardinal Rule: Statelessness
The server does **not** store client session state in memory across requests. If Request 1 creates a case and Request 2 retrieves it, Request 2 must carry all credentials and identifiers required to complete the operation. This enables horizontal scaling: any of 50 backend server containers can handle any request.

## 4. Resource Modeling: Nouns vs. Verbs
The most fundamental principle of REST URI design is: **URIs represent Resources (Nouns), NOT Actions (Verbs).** The action is indicated exclusively by the HTTP Method (`GET`, `POST`, `PUT`, `DELETE`).

| Action Desired | Anti-Pattern (RPC Style - BAD) | RESTful Standard (GOOD) |
|---|---|---|
| Create a new case | `POST /createCase` or `GET /newCase?title=...` | `POST /api/v1/cases` |
| Retrieve case #42 | `GET /getCaseById?id=42` | `GET /api/v1/cases/42` |
| Update case #42 | `POST /updateCaseStatus/42` | `PUT /api/v1/cases/42` or `PATCH /api/v1/cases/42` |
| List all cases | `GET /getAllCases` | `GET /api/v1/cases` |
| Delete case #42 | `GET /deleteCase/42` | `DELETE /api/v1/cases/42` |

## 5. URI Hierarchies & Sub-Resources
When resources have logical parent-child relationships, model them as nested URIs:
- `/api/v1/cases/{case_id}/history` : The audit trail entries belonging to a specific case.
- `/api/v1/users/{user_id}/cases` : The cases created by a specific user.

## 6. How FastAPI Implements REST
FastAPI maps Python functions to REST resources using decorators:
```python
# In app/api/routes/cases.py
router = APIRouter()

# Collection Resource: POST /cases creates a member of the collection
@router.post("/cases", response_model=CaseResponse, status_code=201)
def create_case(case_data: CaseCreate, db: Session = Depends(get_db)):
    ...

# Singleton Resource: GET /cases/{case_id} retrieves a specific member
@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: int, db: Session = Depends(get_db)):
    ...
```

## 7. Common Mistakes
1. **Using Verbs in URIs**:
   - `POST /cases/create` -> Redundant! `POST` already means create. Use `POST /cases`.
2. **Using GET for State Changes**:
   - Sending `GET /cases/delete?id=1` is dangerous! Web crawlers or browser pre-fetching will trigger deletions simply by crawling links.
3. **Inconsistent Pluralization**:
   - Mixing `/case` (singular) and `/users` (plural). Standard convention: **Always use plural nouns** for collections (`/cases`, `/users`).

## 8. Practical Exercises
1. Open [app/api/routes/cases.py](file:///d:/week1_kpmg/case-management-backend/app/api/routes/cases.py). List all exposed endpoint paths. Confirm that every path uses plural nouns and HTTP methods appropriately.
2. Design a RESTful URI hierarchy for adding comments to a case. *(Answer: `POST /api/v1/cases/{case_id}/comments` and `GET /api/v1/cases/{case_id}/comments`)*.

## 9. Interview Questions & Model Answers
**Q: What does it mean for a REST API to be "stateless"?**
*Answer:* Statelessness means that the server retains no client session context between requests. Every individual HTTP request sent to the server must contain all of the contextual information (authentication tokens, resource IDs, parameters) required to understand and fulfill that request. If a load balancer routes Request 1 to Server A and Request 2 to Server B, Server B can fulfill the request without synchronizing in-memory session data with Server A.

## 10. Short Self-Test
1. What is the standard RESTful URI and HTTP method for updating an existing case with ID 10? *(Answer: `PUT /cases/10` or `PATCH /cases/10`).*
2. Why should collections in REST URIs be pluralized (`/cases` instead of `/case`)? *(Answer: To consistently represent the URI as a collection resource from which individual items are retrieved or to which new items are appended).*
