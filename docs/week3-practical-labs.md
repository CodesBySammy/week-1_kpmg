# Week 3 — Practical Hands-on Labs & Exercises

> **Audience:** Fresher AI Engineers & Application Developers  
> **Prerequisites:** Python 3.10+, Virtual Environment activated

---

## Lab 1: Document Parsing & Metadata Extraction

### Objective
Learn how to parse Markdown files with YAML frontmatter, extract key attributes, and clean the text.

### Code
```python
from rag.ingestion.parser import MarkdownDocumentParser

content = """---
document_id: LAB-DOC-001
title: Remote Work Guidelines
category: Human Resources
department: Operations
version: "1.0"
---

# Remote Work Guidelines

## 1. Core Hours
Employees are expected to be online and available during core hours (10:00 AM to 4:00 PM local time).
"""

doc = MarkdownDocumentParser.parse_text(content, default_id="FALLBACK-ID")
print("Parsed Document ID:", doc.document_id)
print("Title:", doc.metadata.title)
print("Department:", doc.metadata.department)
print("Clean Body:\n", doc.raw_content)
```

---

## Lab 2: Comparing Chunking Strategies

### Objective
Observe the difference in chunk boundary placement between Fixed-Size and Markdown Section chunkers.

### Code
```python
from rag.ingestion.parser import DocumentParser
from rag.chunking.strategies import FixedSizeChunker, MarkdownSectionChunker

# Load sample policy
doc = DocumentParser.parse("data/policies/IT-SECURITY-005.md")

# 1. Fixed Size Chunking
fixed = FixedSizeChunker(chunk_size=300, chunk_overlap=50)
fixed_chunks = fixed.split_document(doc)
print(f"Fixed Size produced {len(fixed_chunks)} chunks.")
print("Fixed Chunk 0 Sample:\n", fixed_chunks[0].text[:150], "...\n")

# 2. Markdown Section Chunking
sec_chunker = MarkdownSectionChunker(chunk_size=500, chunk_overlap=100)
sec_chunks = sec_chunker.split_document(doc)
print(f"Markdown Section produced {len(sec_chunks)} chunks.")
print("Section Chunk 1 Title:", sec_chunks[1].section_title)
print("Section Chunk 1 Sample:\n", sec_chunks[1].text[:150], "...\n")
```

---

## Lab 3: Dense Vector Search vs BM25 Keyword Search

### Objective
Query the same document set with Vector Search vs BM25 Keyword Search to observe semantic vs lexical strengths.

### Code
```python
from rag.pipeline import RAGPipeline

p = RAGPipeline()
p.ingest_directory("data/policies")

# Query with technical acronym / exact code
query_exact = "IT-SECURITY-005 section 2.1"
bm25_res = p.retrieve(query=query_exact, mode="bm25", top_k=2)
print("BM25 Top Match:", bm25_res.results[0].chunk.document_id, "| Score:", bm25_res.results[0].score)

# Query with semantic concept
query_semantic = "how can I report financial wrongdoing anonymously?"
vec_res = p.retrieve(query=query_semantic, mode="vector", top_k=2)
print("Vector Top Match:", vec_res.results[0].chunk.document_id, "| Section:", vec_res.results[0].chunk.section_title)
```

---

## Lab 4: Hybrid Retrieval & Fusion

### Objective
Run Hybrid Search with Weighted Fusion ($\alpha = 0.6$) to combine both dense and lexical signals.

### Code
```python
from rag.pipeline import RAGPipeline

p = RAGPipeline()
p.ingest_directory("data/policies")

res = p.retrieve(
    query="What is the daily per diem cap for meals during business trips?",
    mode="hybrid",
    top_k=3,
    use_reranker=True,
)

for item in res.results:
    print(f"Rank {item.rank}: {item.chunk.document_id} [{item.chunk.section_title}]")
    print(f"  Composite Score: {item.score} (Rerank: {item.rerank_score})")
```

---

## Lab 5: Grounded Answer Generation & Refusal Testing

### Objective
Verify that the assistant answers questions grounded in policy context, and refuses out-of-domain questions.

### Code
```python
from rag.pipeline import RAGPipeline
from rag.schemas import RAGRequest

p = RAGPipeline()

# 1. Grounded In-Domain Query
q1 = RAGRequest(question="What are the rules regarding password expiration?")
resp1 = p.answer_question(q1)
print("=== Grounded Response ===")
print("Answer:", resp1.answer)
print("Is Grounded:", resp1.is_grounded)
print("Citations:", [(c.document_id, c.section_title) for c in resp1.citations])

# 2. Out-of-Domain Query
q2 = RAGRequest(question="How do I make chocolate chip cookies?")
resp2 = p.answer_question(q2)
print("\n=== Refusal Response ===")
print("Answer:", resp2.answer)
print("Is Refusal:", resp2.refusal)
```

---

## Lab 6: Running the Benchmark Evaluation

### Objective
Execute the full benchmark suite to calculate Precision@k, Recall@k, and MRR.

### Code
```python
from rag.pipeline import RAGPipeline
from rag.evaluation.evaluator import RAGEvaluator

pipeline = RAGPipeline()
pipeline.ingest_directory("data/policies")

evaluator = RAGEvaluator(pipeline)
comparison = evaluator.compare_retrieval_strategies()

print("Strategy A (Vector Only) MRR:", comparison.strategy_a_metrics.mrr)
print("Strategy B (Hybrid + Reranking) MRR:", comparison.strategy_b_metrics.mrr)
print("\nSummary Analysis:")
print(comparison.summary_analysis)
```
