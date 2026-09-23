# Week 3 — Grounded Policy RAG Knowledge Assistant: Curriculum & Master Study Guide

> **FDE Fresher Readiness Program — Week 3**  
> **Topic:** Retrieval-Augmented Generation (RAG), Vector Indexing, Hybrid Search, Reranking, Grounded Generation, and Evaluation  
> **Status:** Fully Implemented & Tested (100 Tests Passing, 86.78% Code Coverage)

---

## 1. What is RAG and Why Does Enterprise Software Need It?

### 1.1 The Fundamental Limitations of Vanilla LLMs
Large Language Models (LLMs) such as GPT-4, Claude, and Gemini possess vast parametric knowledge acquired during pre-training. However, in enterprise environments (finance, consulting, healthcare, legal), relying solely on raw LLMs introduces critical risks:
1. **Knowledge Cutoff:** An LLM cannot know corporate policies, contracts, or customer data updated yesterday.
2. **Hallucination:** When uncertain, LLMs generate plausible-sounding falsehoods with high confidence.
3. **No Auditable Citations:** Raw LLMs cannot reliably point to page numbers, clause IDs, or document version numbers.
4. **Data Privacy & Leakage:** Retraining or fine-tuning models on proprietary corporate data is computationally prohibitive, slow, and risks leaking confidential client data across organizational boundaries.

### 1.2 The RAG Architecture Solution
Retrieval-Augmented Generation (RAG) decouples **knowledge storage** from **language reasoning**:
- **Non-Parametric Memory (The Retriever):** An external database of policy documents, chunked, indexed, and queryable by semantic vector or keyword match.
- **Parametric Reasoning (The Generator):** A frozen LLM that receives the user's question alongside the retrieved factual excerpts, instructed to answer strictly based on the provided context with exact citations.

```
                      +-----------------------------+
                      |   Corporate Policy Corpus   |
                      | (HR, Finance, IT, Security) |
                      +--------------+--------------+
                                     |
                          [Ingestion & Preprocessing]
                                     |
                          [Chunking & Vectorization]
                                     |
                            +--------v--------+
                            |  Hybrid Index   |
                            | (Vector + BM25) |
                            +--------+--------+
                                     ^
[User Query]                         | 1. Query
     |                               |
     +---->[Retriever & Reranker]----+
     |              |
     |         2. Top-k Relevant Chunks
     v              |
[Context Assembler] <+
(Token Budget Capping)
     |
     v
[Grounded Prompt] -> [LLM Generator] -> [Fact & Citation Verification] -> [Verified Answer with Citations]
```

---

## 2. Ingestion & Preprocessing

### 2.1 Parsing Unstructured Formats
Enterprise documents come in Markdown, Plain Text, HTML, and PDF.
- **Markdown & Frontmatter:** Markdown files frequently contain YAML frontmatter (`--- \n document_id: ... \n ---`). Our `MarkdownDocumentParser` extracts structured metadata (`document_id`, `title`, `category`, `department`, `version`, `effective_date`) before processing body text.
- **PDF Extraction:** PDF documents have layout streams, multi-column text, headers, and footers. `pypdf` extracts per-page content which is normalized before chunking.

### 2.2 Text Normalization Pipeline
Raw text contains inconsistencies that hurt search quality:
- **Whitespace Collapsing:** Replaces Windows `\r\n` with standard `\n`, replaces tabs and non-breaking spaces with spaces, and collapses excessive line breaks while preserving paragraph boundaries.
- **Control Character Stripping:** Removes non-printable ASCII control characters (`\x00-\x1f`) that cause tokenizer bugs or database insertion errors.
- **Token Estimation:** Accurately estimates token count using combined character-to-token heuristics ($\approx 4\text{ chars/token}$) calibrated with word boundaries.

---

## 3. Chunking Strategies & Tradeoffs

Chunking is the single most critical data-engineering step in RAG. Chunk too large, and the context window is flooded with irrelevant noise; chunk too small, and semantic context is severed.

| Strategy | Mechanism | Pros | Cons | Best Use Case |
|---|---|---|---|---|
| **Fixed-Size Chunking** | Splits strictly by $N$ characters/tokens with $M$ overlap | Simple, predictable memory footprint | Splits sentences mid-thought, severs tables and bullet points | Unstructured logs, arbitrary raw text streams |
| **Recursive Character Chunking** | Hierarchically splits by paragraphs (`\n\n`), lines (`\n`), sentences (`. `), words (` `) | Preserves semantic units, prevents broken sentences | Variable chunk lengths, header context can be lost | General prose, FAQs, manuals |
| **Markdown Section Chunking** | Splits along heading boundaries (`#`, `##`, `###`), preserving section titles | Retains document hierarchy, enables section-level citations | Extremely large sections still require sub-chunking | Policy manuals, legal agreements, technical specs |

---

## 4. Embeddings & Vector Search

### 4.1 What is an Embedding?
An embedding model maps unstructured text into a dense vector space $\mathbb{R}^D$ where geometric closeness corresponds to semantic similarity.

### 4.2 Distance Metrics
1. **Cosine Similarity:**
   $$\cos(\mathbf{u}, \mathbf{v}) = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2}$$
   When vectors are pre-normalized to unit length ($\|\mathbf{u}\|_2 = 1$), Cosine Similarity simplifies to the **Dot Product**:
   $$\cos(\mathbf{u}, \mathbf{v}) = \mathbf{u} \cdot \mathbf{v} = \sum_{i=1}^D u_i v_i$$
2. **Euclidean (L2) Distance:**
   $$d(\mathbf{u}, \mathbf{v}) = \sqrt{\sum_{i=1}^D (u_i - v_i)^2}$$
   For unit-normalized vectors: $d^2 = 2 - 2 \cos(\mathbf{u}, \mathbf{v})$. Thus, minimizing L2 distance is mathematically equivalent to maximizing Cosine Similarity.

---

## 5. Lexical Search & BM25

### 5.1 Why Vector Search Alone Fails
Vector embeddings excel at semantic paraphrasing ("inexpensive lodging" $\approx$ "cheap hotels"), but struggle with:
- Exact acronyms and policy IDs (e.g. `IT-SECURITY-005` vs `IT-SECURITY-006`)
- Exact monetary amounts (`$150` vs `$50`)
- Exact clause codes and technical identifiers

### 5.2 Lucene BM25 Formulation
BM25 (Best Matching 25) weights terms based on Inverse Document Frequency (IDF) and normalized Term Frequency (TF):
$$\text{IDF}(t) = \ln\left(1 + \frac{N - n(t) + 0.5}{n(t) + 0.5}\right)$$
$$\text{Score}(D, Q) = \sum_{t \in Q} \text{IDF}(t) \cdot \frac{f(t, D) \cdot (k_1 + 1)}{f(t, D) + k_1 \cdot \left(1 - b + b \cdot \frac{|D|}{\text{avgdl}}\right)}$$
- $k_1 = 1.5$: Governs term frequency saturation.
- $b = 0.75$: Controls document length penalization.

---

## 6. Hybrid Retrieval & Fusion

Hybrid retrieval queries both the dense vector index and sparse BM25 index in parallel, combining candidates using fusion algorithms:

### 6.1 Weighted Score Fusion
$$S_{\text{hybrid}}(d) = \alpha \cdot S_{\text{norm\_vec}}(d) + (1 - \alpha) \cdot S_{\text{norm\_bm25}}(d)$$
Typically, $\alpha = 0.6$ yields an optimal balance between semantic intent and lexical precision.

### 6.2 Reciprocal Rank Fusion (RRF)
RRF combines candidate ranks rather than raw scores, making it immune to differences in score distributions:
$$\text{RRF\_Score}(d) = \sum_{m \in \{\text{Vector}, \text{BM25}\}} \frac{1}{k + \text{Rank}_m(d)}$$
where $k = 60$ is the standard smoothing constant.

---

## 7. Reranking

Reranking applies a scoring pass over the top candidate chunks:
- Evaluates exact multi-word phrase matching
- Computes query term coverage ratio
- Awards bonuses for matches within document and section headers
- Ranks the most authoritative clause to rank 1 before prompt construction.

---

## 8. Controlled Context Assembly & Prompt Engineering

### 8.1 Token Budget Management
If context exceeds the model's budget, the context assembler truncates lower-ranked chunks while preserving complete source blocks for high-scoring chunks.

### 8.2 Structured Source Excerpts
Each chunk is enclosed in an explicit provenance block:
```
[Source 1: IT-SECURITY-005 — Information Security Policy | Section: 2.1 Password Complexity Standards]
All corporate user accounts must enforce a minimum length of 14 characters...
```

### 8.3 Grounding System Instructions
The system prompt strictly commands the LLM:
1. Only answer based on provided facts.
2. Refuse if facts are missing.
3. Include explicit citations for every claim.

---

## 9. Evaluation Metrics for RAG

| Metric | Definition | Purpose |
|---|---|---|
| **Precision@k** | $\frac{\text{Number of relevant retrieved chunks in top } k}{k}$ | Measures noise reduction in context |
| **Recall@k** | $\frac{\text{Number of relevant retrieved chunks in top } k}{\text{Total relevant chunks in corpus}}$ | Measures coverage of essential facts |
| **MRR (Mean Reciprocal Rank)** | $\frac{1}{|Q|} \sum_{i=1}^{|Q|} \frac{1}{\text{Rank of first relevant chunk}}$ | Measures whether the best answer appears at rank 1 |
| **Hit Rate** | Fraction of queries where at least 1 relevant chunk is in top $k$ | Measures retrieval reliability |
| **Faithfulness Score** | Fraction of claims in LLM output substantiated by context | Measures hallucination avoidance |
