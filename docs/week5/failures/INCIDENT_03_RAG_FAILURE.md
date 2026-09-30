# Incident Report: INC-03 - Grounded RAG Retrieval Failure

## 1. Symptom & Description
Users submit queries about topics completely outside the indexed internal compliance and case policy repository (e.g., "What is the capital of France?" or "How do I bake bread?"). In unconstrained LLM setups, the system hallucinated answers with fake case policy citations.

## 2. Expected Behavior
- Hybrid retrieval (Vector + BM25) yields similarity scores below the acceptance threshold (`min_score=0.45`).
- The context assembler identifies an empty retrieval set (`len(retrieved_chunks) == 0`).
- The generation engine deterministically refuses the query with standard refusal message: `"I cannot answer this question based on the provided case documentation."`
- Returns `is_grounded=False`, `citations=[]`, and `refusal=True`.

## 3. Reproduction & Automated Test
Executed via `tests/failure-scenarios/test_failure_scenarios.py::test_rag_failure_empty_retrieval_refuses_gracefully`.

## 4. Root Cause Analysis
System prompts lacked strict negative-constraint instructions, and generator did not gate execution on context token presence.

## 5. Remediation & Hardening
- Implemented strict context gating in `rag/generation/generator.py`: if `not context.formatted_context.strip()`, generator aborts immediately without calling the LLM.
- Enforced citation verification verifying that every citation index corresponds to a chunk in `retrieved_chunks`.
