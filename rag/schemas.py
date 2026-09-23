"""
Pydantic schemas and data models for RAG system.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique identifier of document, e.g. HR-POLICY-001")
    title: str = Field(..., description="Title of document")
    category: str = Field(default="General", description="Category: Human Resources, Finance, IT & Security, etc.")
    policy_type: Optional[str] = Field(default=None, description="Subcategory or policy type")
    version: Optional[str] = Field(default="1.0", description="Document version")
    effective_date: Optional[str] = Field(default=None, description="Effective date in YYYY-MM-DD")
    department: Optional[str] = Field(default=None, description="Owning department")
    last_reviewed: Optional[str] = Field(default=None, description="Last review date")
    status: Optional[str] = Field(default="Active", description="Active, Deprecated, Draft")
    extra: Dict[str, Any] = Field(default_factory=dict, description="Additional custom metadata")


class Document(BaseModel):
    document_id: str
    metadata: DocumentMetadata
    raw_content: str
    source_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Chunk(BaseModel):
    chunk_id: str = Field(..., description="Unique chunk id, e.g., HR-POLICY-001_c001")
    document_id: str
    title: str
    section_title: Optional[str] = None
    section_level: Optional[int] = None
    text: str
    clean_text: str
    chunk_index: int
    char_count: int
    token_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None


class RetrievalQuery(BaseModel):
    query: str
    top_k: int = 5
    retrieval_mode: str = "hybrid"  # vector, bm25, hybrid
    filters: Optional[Dict[str, Any]] = None  # e.g. {"category": "Finance", "department": "Finance"}
    min_score: Optional[float] = 0.0
    use_reranker: bool = False
    rerank_top_k: Optional[int] = 3


class RetrievedChunk(BaseModel):
    chunk: Chunk
    score: float
    vector_score: Optional[float] = None
    bm25_score: Optional[float] = None
    rerank_score: Optional[float] = None
    rank: int


class RetrievalResult(BaseModel):
    query: str
    retrieval_mode: str
    total_candidates_found: int
    results: List[RetrievedChunk]
    execution_time_ms: float
    filters_applied: Optional[Dict[str, Any]] = None


class Citation(BaseModel):
    document_id: str
    title: str
    section_title: Optional[str] = None
    chunk_id: str
    snippet: str
    relevance_score: float


class RAGRequest(BaseModel):
    question: str
    retrieval_mode: str = "hybrid"  # vector, bm25, hybrid
    top_k: int = 4
    filters: Optional[Dict[str, Any]] = None
    use_reranker: bool = True
    temperature: float = 0.0
    strict_grounding: bool = True


class RAGResponse(BaseModel):
    question: str
    answer: str
    is_grounded: bool
    refusal: bool = False
    refusal_reason: Optional[str] = None
    citations: List[Citation]
    retrieved_chunks: List[RetrievedChunk]
    retrieval_mode: str
    execution_time_ms: float
    context_token_count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationMetrics(BaseModel):
    precision_at_k: float
    recall_at_k: float
    mrr: float
    hit_rate: float
    avg_latency_ms: float
    faithfulness_score: Optional[float] = None
    answer_relevance_score: Optional[float] = None


class ComparisonResult(BaseModel):
    strategy_a_name: str
    strategy_a_metrics: EvaluationMetrics
    strategy_b_name: str
    strategy_b_metrics: EvaluationMetrics
    benchmark_queries_count: int
    summary_analysis: str
