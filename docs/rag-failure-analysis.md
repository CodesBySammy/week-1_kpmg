# Week 3 — RAG Failure Modes Analysis & Failure Injection Lab

> **Document Version:** 1.0.0  
> **Topic:** Comprehensive Failure Taxonomy, Edge Cases, Mitigations, and Hands-on Failure Injection Labs

---

## 1. RAG Failure Taxonomy

Enterprise RAG pipelines can fail at five distinct stages. Below is the systematic analysis of failure modes and our implemented architectural mitigations.

```
[Raw Document] -> [Chunker] -> [Index] -> [Retriever] -> [Context Assembler] -> [LLM Generator]
      |               |           |            |                 |                     |
 Stage 1 Fail    Stage 2 Fail  Stage 3 Fail  Stage 4 Fail     Stage 5 Fail         Stage 6 Fail
 (Ingestion)      (Chunking)   (Indexing)    (Retrieval)      (Context Assembly)   (Generation)
```

---

### Failure Stage 1: Ingestion & Parsing Errors
* **Failure Mode 1.1: Malformed YAML Frontmatter:** YAML delimiters (`---`) corrupted or containing unescaped colons.
  * *Impact:* Document parser crashes or drops metadata.
  * *Mitigation in Code:* `MarkdownDocumentParser.parse_text` wraps `yaml.safe_load` in a `try...except` block, safely falling back to document defaults and header-based title extraction without crashing.
* **Failure Mode 1.2: Corrupted or Password-Protected PDFs:** Non-extractable text streams or encrypted files.
  * *Mitigation in Code:* `PDFDocumentParser.parse_file` wraps page iteration and catches exceptions, logging a structured warning and embedding an explicit error node.
* **Failure Mode 1.3: Hidden Control Characters:** Non-printable null bytes (`\x00`) or escape sequences breaking database engines.
  * *Mitigation in Code:* `DocumentPreprocessor.clean_text` applies regex sanitizer `[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]` before any downstream processing.

---

### Failure Stage 2: Chunking & Boundary Severing
* **Failure Mode 2.1: Splitting Sentences Mid-Thought (Fixed-Size Chunking):**
  * *Impact:* Condition clauses (e.g. *"Only with prior manager approval"* severed from *"Employees may expense up to $500"*).
  * *Mitigation in Code:* Implemented `MarkdownSectionChunker` which anchors chunks at header boundaries (`#`, `##`, `###`), preserving entire rule clauses within single coherent chunks.
* **Failure Mode 2.2: Context Severing (Lost Header Context):**
  * *Impact:* A chunk stating *"Max 5 days rollover"* without knowing whether it applies to Sick Leave or Annual Leave.
  * *Mitigation in Code:* The chunker prefixes section titles into chunk metadata and embeds `## {header_name}\n{body}` directly into the chunk text.

---

### Failure Stage 3: Retrieval Failures
* **Failure Mode 3.1: Lexical Blindness (Vector-Only Failure):**
  * *Query:* *"What is policy IT-SECURITY-005 section 2.1?"*
  * *Vector Behavior:* Matches general security phrases, missing the exact clause.
  * *Mitigation in Code:* Hybrid search combines dense vectors with Lucene BM25 keyword matching, ensuring exact code matches receive maximum lexical rank.
* **Failure Mode 3.2: Negative IDF Anomaly in Small Collections:**
  * *Standard BM25Okapi Behavior:* When a word appears in >50% of documents in a tiny corpus, Robertson-Spärck Jones IDF becomes zero or negative.
  * *Mitigation in Code:* We implemented Lucene's non-negative smoothed IDF formula $\ln(1 + \frac{N - n + 0.5}{n + 0.5})$, guaranteeing non-negative scores.

---

### Failure Stage 4: Context Assembly & Token Overflow
* **Failure Mode 4.1: Prompt Budget Overflow:**
  * *Impact:* Sending 10 retrieved chunks exceeds context window, resulting in API 400 errors.
  * *Mitigation in Code:* `ContextAssembler` enforces strict `max_context_tokens` (default 2000), iteratively accumulating chunks and cleanly dropping lower-ranked chunks that exceed budget.
* **Failure Mode 4.2: Duplicate Passage Redundancy:**
  * *Impact:* Multiple chunks from overlapping headers waste context tokens.
  * *Mitigation in Code:* Hash-based passage deduplication in `ContextAssembler.assemble`.

---

### Failure Stage 5: Generation & Hallucination Failures
* **Failure Mode 5.1: Extrapolation on Out-of-Domain Questions:**
  * *Query:* *"How do I make chocolate chip cookies?"*
  * *Ungrounded Model:* Hallucinates a recipe or claims it is in corporate policy.
  * *Mitigation in Code:* `MockLLMProvider` and `GroundedAnswerGenerator` evaluate meaningful term overlap between question and context. If context contains zero related facts, the system emits an explicit refusal: *"I am unable to answer this question based on the provided policy documents."*
* **Failure Mode 5.2: Phantom Citations (Hallucinated Source References):**
  * *Impact:* Model answers correctly but cites non-existent policies `[HR-POLICY-999]`.
  * *Mitigation in Code:* `_extract_and_verify_citations()` cross-checks every bracketed citation against `context.citation_index`. If a citation cannot be resolved to an actual retrieved chunk, it is flagged as ungrounded (`is_grounded = False`).

---

## 2. Practical Failure Injection Lab

Run these experiments in your virtual environment to verify failure handling:

### Experiment 1: Ingestion of Corrupted Markdown
```python
from rag.ingestion.parser import MarkdownDocumentParser

corrupted_yaml = """---
document_id: [CORRUPT_YAML: {unclosed: mapping
status: Active
---
# Corrupted Document
Body text here.
"""

doc = MarkdownDocumentParser.parse_text(corrupted_yaml, default_id="RECOVERY-DOC")
assert doc.document_id == "RECOVERY-DOC"
print("Experiment 1 Passed: Corrupted YAML gracefully defaulted without crashing!")
```

### Experiment 2: Out-of-Domain Refusal Verification
```python
from rag.pipeline import RAGPipeline
from rag.schemas import RAGRequest

p = RAGPipeline()
resp = p.answer_question(RAGRequest(question="What is the average airspeed velocity of an unladen swallow?"))
assert resp.refusal is True
print("Experiment 2 Passed: Out-of-domain query triggered formal refusal!")
```

### Experiment 3: Context Overflow Truncation
```python
from rag.context.assembler import ContextAssembler
from rag.schemas import Chunk, RetrievedChunk

chunks = [
    RetrievedChunk(chunk=Chunk(chunk_id=f"C{i}", document_id="D1", title="T", text="Sample policy text "*50, clean_text="Sample policy text "*50, chunk_index=i, char_count=900, token_count=200), score=1.0/(i+1), rank=i+1)
    for i in range(15)
]

assembler = ContextAssembler(max_context_tokens=400)
ctx = assembler.assemble(chunks)
assert ctx.total_tokens <= 450
assert ctx.dropped_chunk_count > 0
print(f"Experiment 3 Passed: Successfully dropped {ctx.dropped_chunk_count} chunks to protect token budget!")
```
