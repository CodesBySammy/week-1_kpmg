# Week 3: Grounded Policy RAG Architecture

## 1. System Overview
The Week 3 Grounded Policy RAG service is an enterprise-grade retrieval and question-answering system operating over corporate policy manuals. It couples dual dense and sparse search indices with candidate reranking, token-bounded context assembly, and zero-hallucination generation.

## 2. Component Pipeline
```mermaid
graph TD
    Corpus[Corporate Policy Corpus: data/policies/] --> Parser[Markdown & PDF Parser]
    Parser --> Preproc[Text Sanitizer & Normalizer]
    Preproc --> Chunker[Markdown Section Chunker]
    
    Chunker --> DenseIdx[Dense Vector Index: 384-dim Cosine]
    Chunker --> SparseIdx[BM25 Index: Lucene Smoothed]
    
    Query[User Query / Case Policy Check] --> Retriever[Hybrid Retriever]
    Retriever --> DenseIdx
    Retriever --> SparseIdx
    
    DenseIdx --> Fusion[Weighted Score Fusion alpha=0.6]
    SparseIdx --> Fusion
    
    Fusion --> Reranker[CrossScore Candidate Reranker]
    Reranker --> Assembler[Token-Bounded Context Assembler]
    Assembler --> LLMGen[Grounded Answer Generator]
    LLMGen --> CitationVerifier[Citation Attribution Engine]
    CitationVerifier --> Response[Verified Answer with Citations]
```
