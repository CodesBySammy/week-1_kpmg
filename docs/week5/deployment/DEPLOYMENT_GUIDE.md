# Enterprise Deployment Guide (v1.0.0-rc1)

## 1. Prerequisites
- Docker Engine 24.0+ / Kubernetes 1.28+
- Python 3.14.7 runtime environment (if deploying directly to bare metal / VM)
- PostgreSQL 15+ (or managed AWS RDS / Azure Database for PostgreSQL)

## 2. Docker Deployment

### Step 1: Build the Container Image
```bash
docker build -t case-management-backend:1.0.0-rc1 -f deployment/Dockerfile .
```

### Step 2: Configure Environment
Copy `.env.example` to `.env` and populate production secrets:
```bash
DATABASE_URL=postgresql://dbuser:StrongPassword@db-host:5432/casemgmt
JWT_SECRET_KEY=production-secure-32-byte-hex-key
APPROVAL_SECRET_KEY=production-secure-hmac-key
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Step 3: Run Container
```bash
docker run -d --name case-mgmt-app \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  case-management-backend:1.0.0-rc1
```

### Step 4: Verify Deployment Health
```bash
curl -f http://localhost:8000/health/ready
# Expected: {"status": "ready", "database": "connected", "rag_index": "initialized"}
```
