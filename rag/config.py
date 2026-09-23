"""
Configuration settings for RAG components.
"""
from pathlib import Path
from pydantic_settings import BaseSettings


class RAGSettings(BaseSettings):
    # Storage and paths
    corpus_dir: Path = Path("data/policies")
    index_storage_dir: Path = Path("data/indices")
    
    # Chunking settings
    chunk_size: int = 500
    chunk_overlap: int = 100
    chunking_strategy: str = "markdown_section"  # markdown_section, recursive, fixed
    
    # Embedding settings
    embedding_provider: str = "dense_hash"  # dense_hash, sentence_transformers, mock
    embedding_dimension: int = 384
    
    # Retrieval settings
    default_top_k: int = 5
    similarity_threshold: float = 0.25
    retrieval_mode: str = "hybrid"  # vector, bm25, hybrid
    hybrid_alpha: float = 0.6  # weight for vector score in hybrid (1 - alpha for bm25)
    rrf_k: int = 60  # constant for Reciprocal Rank Fusion
    
    # Reranking settings
    use_reranker: bool = True
    rerank_top_k: int = 3
    
    # Context Assembly settings
    max_context_tokens: int = 2000
    include_metadata_header: bool = True
    
    # Generation settings
    llm_provider: str = "mock"  # mock, openai
    llm_model: str = "mock-gpt-4o"
    temperature: float = 0.0
    require_citations: bool = True
    strict_grounding: bool = True
    
    model_config = {
        "env_prefix": "RAG_",
        "extra": "ignore",
    }


rag_settings = RAGSettings()
