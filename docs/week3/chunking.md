# Document Chunking Strategies & Evaluations

## 1. Chunking Strategies Implemented
1. **Fixed-Size Chunker (`FixedSizeChunker`):** Splits text by character or token size with configurable overlap.
2. **Recursive Character Chunker (`RecursiveCharacterChunker`):** Recursively splits along paragraphs (`\n\n`), lines (`\n`), and sentence boundaries.
3. **Markdown Section Chunker (`MarkdownSectionChunker`):** Splits along markdown header boundaries (`#`, `##`, `###`), preserving section titles, structural hierarchy, and complete policy clauses.

## 2. Evaluation Findings
Markdown Section Chunking achieved **100% Hit Rate** and **0.9167 MRR** in our benchmark evaluation, outperforming fixed-size chunking which severed critical condition clauses from their parent policy rules.
