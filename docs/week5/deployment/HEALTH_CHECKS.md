# Platform Health Checks & Readiness Probes

## 1. Liveness Probe (`GET /health/live`)
- **Purpose**: Verifies that the ASGI worker process is alive and responding to HTTP requests.
- **Kubernetes Spec**:
  ```yaml
  livenessProbe:
    httpGet:
      path: /health/live
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 10
  ```
- **Response**: `HTTP 200 OK` `{"status": "alive"}`

## 2. Readiness Probe (`GET /health/ready`)
- **Purpose**: Verifies that the application has established database connectivity, loaded configuration, and initialized the RAG vector index.
- **Kubernetes Spec**:
  ```yaml
  readinessProbe:
    httpGet:
      path: /health/ready
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 5
  ```
- **Response**: `HTTP 200 OK` `{"status": "ready", "database": "ok", "rag": "ok"}`
