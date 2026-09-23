"""
End-to-end RAG Pipeline orchestrator for Policy Knowledge Assistant.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import time

from rag.config import RAGSettings, rag_settings
from rag.schemas import (
    Document,
    Chunk,
    RetrievalQuery,
    RetrievalResult,
    RAGRequest,
    RAGResponse,
)
from rag.ingestion.parser import DocumentParser
from rag.chunking.strategies import get_chunker
from rag.embeddings.providers import get_embedding_provider
from rag.indexing.hybrid_index import HybridIndex
from rag.retrieval.reranker import get_reranker
from rag.retrieval.retriever import Retriever
from rag.context.assembler import ContextAssembler
from rag.llm.provider import get_llm_provider
from rag.generation.generator import GroundedAnswerGenerator


class RAGPipeline:
    """
    Unified enterprise RAG pipeline:
    Ingestion -> Chunking -> Indexing -> Retrieval -> Reranking -> Context Assembly -> Grounded Generation.
    """

    def __init__(self, settings: Optional[RAGSettings] = None):
        self.settings = settings or rag_settings

        # 1. Chunking
        self.chunker = get_chunker(
            strategy=self.settings.chunking_strategy,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        # 2. Embeddings
        self.embedding_provider = get_embedding_provider(
            provider_type=self.settings.embedding_provider,
            dimension=self.settings.embedding_dimension,
        )

        # 3. Indices
        self.index = HybridIndex(embedding_provider=self.embedding_provider)

        # 4. Reranker & Retriever
        self.reranker = get_reranker("cross_score") if self.settings.use_reranker else None
        self.retriever = Retriever(index=self.index, reranker=self.reranker)

        # 5. Context Assembler
        self.context_assembler = ContextAssembler(
            max_context_tokens=self.settings.max_context_tokens,
            include_metadata_header=self.settings.include_metadata_header,
        )

        # 6. LLM Provider & Generator
        self.llm_provider = get_llm_provider(
            provider_type=self.settings.llm_provider,
            model_name=self.settings.llm_model,
        )
        self.generator = GroundedAnswerGenerator(llm_provider=self.llm_provider)

        self._is_indexed = False
        self.documents: List[Document] = []
        self.chunks: List[Chunk] = []

    def ingest_directory(self, dir_path: Optional[Union[str, Path]] = None) -> int:
        """
        Parses all policy documents in the directory, chunks them, and builds indices.
        Returns the number of chunks indexed.
        """
        target_dir = Path(dir_path or self.settings.corpus_dir)
        self.documents = DocumentParser.load_directory(target_dir)

        all_chunks: List[Chunk] = []
        for doc in self.documents:
            doc_chunks = self.chunker.split_document(doc)
            all_chunks.extend(doc_chunks)

        self.chunks = all_chunks
        self.index.add_chunks(all_chunks)
        self._is_indexed = True

        return len(all_chunks)

    def retrieve(self, query: str, mode: str = "hybrid", top_k: int = 5, filters: Optional[Dict[str, Any]] = None, use_reranker: bool = True) -> RetrievalResult:
        """Runs candidate retrieval directly without generation."""
        if not self._is_indexed:
            self.ingest_directory()

        req = RetrievalQuery(
            query=query,
            top_k=top_k,
            retrieval_mode=mode,
            filters=filters,
            use_reranker=use_reranker,
            rerank_top_k=top_k,
        )
        return self.retriever.retrieve(req)

    def answer_question(self, request: RAGRequest) -> RAGResponse:
        """
        Executes complete RAG workflow for a user query:
        Retrieves top relevant chunks -> assembles prompt context -> calls LLM -> returns verified response.
        """
        start_time = time.perf_counter()

        if not self._is_indexed:
            self.ingest_directory()

        # Step 1: Retrieval
        query_obj = RetrievalQuery(
            query=request.question,
            top_k=request.top_k,
            retrieval_mode=request.retrieval_mode,
            filters=request.filters,
            use_reranker=request.use_reranker,
            rerank_top_k=request.top_k,
        )
        retrieval_res = self.retriever.retrieve(query_obj)

        # Step 2: Context Assembly
        assembled_context = self.context_assembler.assemble(retrieval_res.results)

        # Step 3: Grounded Answer Generation
        answer, citations, is_grounded, is_refusal = self.generator.generate_answer(
            question=request.question,
            context=assembled_context,
            temperature=request.temperature,
            strict_grounding=request.strict_grounding,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return RAGResponse(
            question=request.question,
            answer=answer,
            is_grounded=is_grounded,
            refusal=is_refusal,
            refusal_reason="Insufficient policy context found" if is_refusal else None,
            citations=citations,
            retrieved_chunks=assembled_context.included_chunks,
            retrieval_mode=request.retrieval_mode,
            execution_time_ms=round(elapsed_ms, 2),
            context_token_count=assembled_context.total_tokens,
            metadata={
                "documents_in_corpus": len(self.documents),
                "total_chunks_in_index": len(self.chunks),
                "dropped_chunks_from_budget": assembled_context.dropped_chunk_count,
            },
        )
