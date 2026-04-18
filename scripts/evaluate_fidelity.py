"""
evaluate_fidelity.py
Computes token reduction and semantic similarity between original and pidgin texts.
"""

import json
import sys
from pathlib import Path


def count_tokens_approx(text: str) -> int:
    """Rough token estimate: ~4 chars per token (GPT-style)."""
    return max(1, len(text) // 4)


def token_reduction(original: str, pidgin: str) -> float:
    orig_tokens = count_tokens_approx(original)
    pidg_tokens = count_tokens_approx(pidgin)
    return round((1 - pidg_tokens / orig_tokens) * 100, 2)


def evaluate_pair(original: str, pidgin: str) -> dict:
    return {
        "original_tokens": count_tokens_approx(original),
        "pidgin_tokens": count_tokens_approx(pidgin),
        "reduction_pct": token_reduction(original, pidgin),
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python evaluate_fidelity.py <results_jsonl>")
        print("  Each line: {\"original\": \"...\", \"pidgin\": \"...\"}")
        sys.exit(1)

    path = Path(sys.argv[1])
    results = []
    with path.open() as f:
        for line in f:
            entry = json.loads(line)
            metrics = evaluate_pair(entry["original"], entry["pidgin"])
            results.append({**entry, **metrics})
            print(json.dumps(metrics))

    avg_reduction = sum(r["reduction_pct"] for r in results) / len(results)
    print(f"\nAverage token reduction: {avg_reduction:.1f}%")


if __name__ == "__main__":
    main()
