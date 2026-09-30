# Technical Presentation Notes (For Engineering Stakeholders)

- **Architecture**: Asynchronous FastAPI service decoupled into domain services, lakehouse ingestion pipelines, hybrid RAG subsystem, and LangGraph-style workflow orchestrator.
- **Design Philosophy**: Deterministic application code is the final arbiter of security and state. AI models are strictly proposal generators.
- **Extensibility**: Plug-and-play architecture for embedding models, vector stores, and external tool registries via abstract base classes.
