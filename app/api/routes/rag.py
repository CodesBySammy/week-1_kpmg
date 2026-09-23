"""
RAG API routes for the Corporate Policy Knowledge Assistant.
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.case import Case
from rag.pipeline import RAGPipeline
from rag.schemas import (
    RAGRequest,
    RAGResponse,
    RetrievalQuery,
    RetrievalResult,
    ComparisonResult,
    DocumentMetadata,
)
from rag.evaluation.evaluator import RAGEvaluator

router = APIRouter(prefix="/rag", tags=["Policy RAG Assistant"])

# Global pipeline instance (lazily initialized on first use)
_pipeline_instance: Optional[RAGPipeline] = None


def get_rag_pipeline() -> RAGPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = RAGPipeline()
        _pipeline_instance.ingest_directory()
    return _pipeline_instance


@router.get("/policies", response_model=List[DocumentMetadata], summary="List all indexed policies")
def list_policies(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """Returns metadata for all policy documents currently loaded into the RAG corpus."""
    return [doc.metadata for doc in pipeline.documents]


@router.post("/ingest", summary="Ingest policy documents from corpus")
def ingest_corpus(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """Triggers ingestion and re-indexing of all policy documents."""
    chunk_count = pipeline.ingest_directory()
    return {
        "status": "success",
        "documents_indexed": len(pipeline.documents),
        "chunks_indexed": chunk_count,
    }


@router.post("/retrieve", response_model=RetrievalResult, summary="Retrieve relevant policy chunks")
def retrieve_chunks(
    query_obj: RetrievalQuery, pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Retrieves matching policy chunks without LLM generation.
    Supports retrieval_mode: 'vector', 'bm25', 'hybrid', with metadata filtering and reranking.
    """
    return pipeline.retriever.retrieve(query_obj)


@router.post("/query", response_model=RAGResponse, summary="Ask grounded question to Policy Assistant")
def ask_policy_assistant(
    request: RAGRequest, pipeline: RAGPipeline = Depends(get_rag_pipeline)
):
    """
    Executes grounded RAG pipeline:
    Retrieves chunks -> builds token-bounded context -> generates grounded answer with verified citations.
    """
    return pipeline.answer_question(request)


@router.get("/benchmark", response_model=ComparisonResult, summary="Run retrieval benchmark comparison")
def run_benchmark(pipeline: RAGPipeline = Depends(get_rag_pipeline)):
    """
    Evaluates Strategy A (Vector-only) vs Strategy B (Hybrid + Reranking)
    on standard benchmark queries and returns comprehensive metrics.
    """
    evaluator = RAGEvaluator(pipeline)
    return evaluator.compare_retrieval_strategies()


@router.post("/cases/{case_id}/policy-check", summary="Check case compliance against corporate policies")
def check_case_compliance(
    case_id: int,
    db: Session = Depends(get_db),
    pipeline: RAGPipeline = Depends(get_rag_pipeline),
):
    """
    Integrated Week 1 + Week 3 endpoint:
    Fetches a case by ID from SQLite, formulates an automated policy compliance query,
    and returns authoritative policy guidance.
    """
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case with ID {case_id} not found.",
        )

    compliance_query = (
        f"Case Title: {case.title}. Case Description: {case.description or case.title}. "
        f"Identify applicable corporate policies, compliance rules, thresholds, or required approvals."
    )

    req = RAGRequest(
        question=compliance_query,
        retrieval_mode="hybrid",
        top_k=4,
        use_reranker=True,
    )
    rag_resp = pipeline.answer_question(req)

    return {
        "case_id": case.id,
        "case_title": case.title,
        "case_priority": case.priority.value if hasattr(case.priority, "value") else str(case.priority),
        "case_status": case.status.value if hasattr(case.status, "value") else str(case.status),
        "policy_advice": rag_resp.answer,
        "is_grounded": rag_resp.is_grounded,
        "citations": [
            {
                "document_id": c.document_id,
                "title": c.title,
                "section": c.section_title,
                "relevance_score": c.relevance_score,
            }
            for c in rag_resp.citations
        ],
    }
