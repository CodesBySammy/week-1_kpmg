# LAB-02: Cross-Layer Architectural Design & Mermaid Modeling

## 1. Objective
Model an enterprise AI platform architecture including gateway, security, workflow, RAG, and persistence layers using Mermaid diagrams.

## 2. Prerequisites
Understanding of microservices, clean architecture, and Mermaid markdown syntax.

## 3. Practical Task
Construct component, sequence, deployment, and data flow diagrams representing the integrated platform.

## 4. Step-by-Step Instructions
1. Open `docs/week5/architecture/COMPONENT_DIAGRAM.md`.
2. Identify the boundary between the workflow orchestrator and tool executor.
3. Draft a sequence diagram for human approval.
4. Render diagrams in markdown preview.

## 5. Expected Result
Accurate Mermaid diagrams mapping 1-to-1 with active Python modules in `app/`, `rag/`, and `workflow/`.

## 6. Verification & Automated Validation
Verify syntax rendering with no syntax errors in IDE preview.

## 7. Challenge Questions
How does the sequence diagram change if the supervisor rejects the approval request?
