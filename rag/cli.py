"""
Command-Line Interface (CLI) for RAG Policy Knowledge Assistant.
Usage:
    python -m rag.cli ingest [--dir DIR]
    python -m rag.cli query "What is the password policy?" [--mode hybrid] [--top-k 3]
    python -m rag.cli evaluate
"""
import argparse
import sys
import json
import time

from rag.pipeline import RAGPipeline
from rag.schemas import RAGRequest, RetrievalQuery
from rag.evaluation.evaluator import RAGEvaluator


def cmd_ingest(args):
    print("=" * 60)
    print("RAG Corpus Ingestion & Vector Indexing")
    print("=" * 60)
    pipeline = RAGPipeline()
    t0 = time.perf_counter()
    num_chunks = pipeline.ingest_directory(args.dir)
    elapsed = time.perf_counter() - t0
    print(f"Indexed {len(pipeline.documents)} documents into {num_chunks} chunks.")
    print(f"Indices updated: VectorIndex (dense) + BM25Index (lexical)")
    print(f"Completed in {elapsed:.2f} seconds.")


def cmd_query(args):
    print("=" * 60)
    print(f"Policy Knowledge Query: '{args.question}'")
    print(f"Mode: {args.mode} | Top-K: {args.top_k} | Reranker: {not args.no_rerank}")
    print("=" * 60)
    pipeline = RAGPipeline()
    req = RAGRequest(
        question=args.question,
        retrieval_mode=args.mode,
        top_k=args.top_k,
        use_reranker=not args.no_rerank,
    )
    resp = pipeline.answer_question(req)

    print("\n--- GROUNDED ANSWER ---")
    print(resp.answer)
    print(f"\nGrounding Status: {'Grounded in Context' if resp.is_grounded else 'Warning: Potential Hallucination'}")
    print(f"Refusal Status: {resp.refusal}")
    print(f"Execution Latency: {resp.execution_time_ms} ms")
    print(f"Context Tokens: {resp.context_token_count}")

    if resp.citations:
        print("\n--- VERIFIED CITATIONS ---")
        for i, c in enumerate(resp.citations, 1):
            sec = f" | Section: {c.section_title}" if c.section_title else ""
            print(f"[{i}] {c.document_id} — {c.title}{sec}")
            print(f"    Snippet: \"{c.snippet[:120]}...\"")

    if args.verbose:
        print("\n--- RETRIEVED CHUNKS ---")
        for r in resp.retrieved_chunks:
            print(f"- Rank {r.rank} [{r.chunk.chunk_id}] Score: {r.score} (Rerank: {r.rerank_score})")


def cmd_evaluate(args):
    print("=" * 60)
    print("RAG Retrieval & Generation Benchmark Evaluation")
    print("Strategy A (Vector Only k=5) vs Strategy B (Hybrid + Reranking k=3)")
    print("=" * 60)
    pipeline = RAGPipeline()
    evaluator = RAGEvaluator(pipeline)
    t0 = time.perf_counter()
    comparison = evaluator.compare_retrieval_strategies()
    elapsed = time.perf_counter() - t0

    print(f"\nBenchmark Queries Evaluated: {comparison.benchmark_queries_count}")
    print(f"Execution Time: {elapsed:.2f}s\n")

    print(f"{'Metric':<25} | {'Strategy A (Vector)':<22} | {'Strategy B (Hybrid+Rerank)':<25}")
    print("-" * 78)
    mA = comparison.strategy_a_metrics
    mB = comparison.strategy_b_metrics
    print(f"{'Hit Rate':<25} | {mA.hit_rate*100:>20.1f}% | {mB.hit_rate*100:>23.1f}%")
    print(f"{'MRR (Mean Reciprocal Rank)':<25} | {mA.mrr:>21.4f} | {mB.mrr:>24.4f}")
    print(f"{'Precision@k':<25} | {mA.precision_at_k:>21.4f} | {mB.precision_at_k:>24.4f}")
    print(f"{'Recall@k':<25} | {mA.recall_at_k:>21.4f} | {mB.recall_at_k:>24.4f}")
    print(f"{'Avg Latency (ms)':<25} | {mA.avg_latency_ms:>20.2f}ms | {mB.avg_latency_ms:>23.2f}ms")
    print(f"{'Faithfulness Score':<25} | {mA.faithfulness_score:>21.4f} | {mB.faithfulness_score:>24.4f}")
    print("-" * 78)
    print("\nSummary Analysis:")
    print(comparison.summary_analysis)


def main():
    parser = argparse.ArgumentParser(description="Corporate Policy RAG CLI")
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to execute")

    # Ingest
    p_ingest = subparsers.add_parser("ingest", help="Ingest and index policy documents")
    p_ingest.add_argument("--dir", default="data/policies", help="Directory containing policy files")

    # Query
    p_query = subparsers.add_parser("query", help="Ask a question against policy corpus")
    p_query.add_argument("question", type=str, help="Question to query")
    p_query.add_argument("--mode", default="hybrid", choices=["vector", "bm25", "hybrid"], help="Retrieval mode")
    p_query.add_argument("--top-k", type=int, default=3, help="Number of chunks to retrieve")
    p_query.add_argument("--no-rerank", action="store_true", help="Disable candidate reranker")
    p_query.add_argument("-v", "--verbose", action="store_true", help="Display retrieved chunk details")

    # Evaluate
    p_eval = subparsers.add_parser("evaluate", help="Run comparative benchmark evaluation")

    args = parser.parse_args()

    if args.command == "ingest":
        cmd_ingest(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "evaluate":
        cmd_evaluate(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
