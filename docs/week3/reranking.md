# Candidate Reranking Architecture

## 1. The Need for Reranking
First-stage hybrid retrieval retrieves candidate passages based on overall similarity. However, the exact clause that answers the user's specific inquiry may be ranked 3rd or 4th due to document length or generalized vocabulary.

## 2. CrossScore Reranker (`CrossScoreReranker`)
The reranker scores candidate chunks using:
1. Exact keyword coverage ratio.
2. Contiguous phrase match bonuses.
3. Section title alignment.
4. Promotion of exact rule matches to Rank 1.
In benchmark evaluations, this raised MRR from **0.6292 to 0.9167 (+45.7%)**.
