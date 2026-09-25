# System Component Diagram

The following Mermaid diagram details the high-level architecture of the Enterprise Case Management Platform, depicting interactions between clients, security middleware, domain services, RAG, agentic tools, and persistent storage.

```mermaid
graph TD
    Client[Client Applications / API Consumers] -->|HTTP / REST + Bearer JWT| APIGateway[FastAPI Gateway]
    
    subgraph Security & Middleware
        APIGateway --> CorrMiddleware[Correlation ID Middleware]
        CorrMiddleware --> AuthGuard[JWT Auth & RBAC Guard]
        AuthGuard --> SecGuardrails[Prompt Injection & Input Guardrails]
    end

    subgraph Workflow & Agentic Layer
        SecGuardrails --> Router[Deterministic Workflow Router]
        Router -->|Intent: Policy Q&A| RAGService[Grounded RAG Engine]
        Router -->|Intent: Case Inspection| ToolExecutor[Agentic Tool Orchestrator]
        Router -->|Intent: Case Modification| ApprovalCheck{Human Approval Required?}
        ApprovalCheck -->|Token Missing| StateHalt[State: WAITING_FOR_APPROVAL]
        ApprovalCheck -->|Valid Token| ToolExecutor
    end

    subgraph Tool Integration Layer
        ToolExecutor --> ToolRead[retrieve_case Tool]
        ToolExecutor --> ToolWrite[update_ticket Tool]
    end

    subgraph RAG Subsystem
        RAGService --> VectorIndex[Dense Vector Hash Index]
        RAGService --> BM25Index[Sparse BM25 Index]
        VectorIndex --> Reranker[Cross-Score Reranker]
        BM25Index --> Reranker
        Reranker --> GroundedGen[Grounded Generator + Citations]
    end

    subgraph Data & Storage Layer
        ToolRead --> CaseRepo[SQLAlchemy Case Repository]
        ToolWrite --> CaseRepo
        CaseRepo --> SQLiteDB[(SQLite Relational DB)]
        CaseRepo --> AuditLog[(Audit Log Store)]
    end

    subgraph Observability
        APIGateway -.-> Logger[Structured JSON Logger]
        ToolExecutor -.-> Tracer[OpenTelemetry Tracing]
        Router -.-> MetricsCollector[Prometheus Metrics]
    end
```
