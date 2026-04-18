"""
LLM Pidgin — Token Compression Benchmark
token_counter.py

Counts tokens for natural language and LLM Pidgin versions of each test case
across all available tokenizers, then produces summary statistics and plots.

Usage:
    python token_counter.py --input test_cases.csv --output results/

Requirements:
    pip install tiktoken transformers sentencepiece pandas matplotlib seaborn tqdm
"""

import argparse
import csv
import json
import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import pandas as pd

# ── TOKENIZER REGISTRY ────────────────────────────────────────────────────────

def load_tiktoken(encoding_name):
    import tiktoken
    enc = tiktoken.get_encoding(encoding_name)
    return lambda text: len(enc.encode(text))

def load_hf_tokenizer(model_id):
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    return lambda text: len(tok.encode(text))

TOKENIZER_REGISTRY = {
    # tiktoken — no auth
    "gpt4_cl100k":    ("tiktoken",      "cl100k_base"),
    "gpt4o_o200k":    ("tiktoken",      "o200k_base"),
    # HuggingFace — no auth
    "mistral_7b":     ("huggingface",   "mistralai/Mistral-7B-v0.1"),
    "mistral_nemo":   ("huggingface",   "mistralai/Mistral-Nemo-Base-2407"),
    "qwen2_7b":       ("huggingface",   "Qwen/Qwen2-7B"),
    "phi3_mini":      ("huggingface",   "microsoft/Phi-3-mini-4k-instruct"),
    "phi3_medium":    ("huggingface",   "microsoft/Phi-3-medium-4k-instruct"),
    "deepseek_v2":    ("huggingface",   "deepseek-ai/DeepSeek-V2"),
    "command_r":      ("huggingface",   "CohereForAI/c4ai-command-r-v01"),
    # HuggingFace — requires account / acceptance
    "gemma2_9b":      ("huggingface",   "google/gemma-2-9b"),
    "llama3_8b":      ("huggingface",   "meta-llama/Meta-Llama-3-8B"),
    "llama3_70b":     ("huggingface",   "meta-llama/Meta-Llama-3-70B"),
}


def build_tokenizers(verbose=True):
    """Attempt to load all tokenizers. Skip gracefully if unavailable."""
    loaded = {}
    skipped = {}

    for name, (kind, identifier) in TOKENIZER_REGISTRY.items():
        try:
            if kind == "tiktoken":
                fn = load_tiktoken(identifier)
            else:
                fn = load_hf_tokenizer(identifier)
            # smoke test
            fn("hello world")
            loaded[name] = fn
            if verbose:
                print(f"  ✓ {name}")
        except Exception as e:
            skipped[name] = str(e)
            if verbose:
                print(f"  ✗ {name} — {type(e).__name__}: {str(e)[:80]}")

    return loaded, skipped


# ── COUNTING ──────────────────────────────────────────────────────────────────

def count_tokens(text, tokenizer_fn):
    """Count tokens, return -1 on error."""
    try:
        return tokenizer_fn(str(text))
    except Exception:
        return -1


def run_counts(df, tokenizers, verbose=True):
    """
    For each row in df, count tokens for nl_text and pidgin_text
    across all tokenizers.

    Returns a long-form DataFrame with columns:
        id, tier, setting, entity_count,
        tokenizer, nl_tokens, pidgin_tokens, compression_ratio,
        nl_chars, pidgin_chars, char_ratio
    """
    rows = []
    total = len(df) * len(tokenizers)
    done = 0

    for _, row in df.iterrows():
        nl = str(row["nl_text"])
        pidgin = str(row["pidgin_text"])
        nl_chars = len(nl)
        pidgin_chars = len(pidgin)
        char_ratio = round(nl_chars / pidgin_chars, 4) if pidgin_chars > 0 else None

        for tok_name, tok_fn in tokenizers.items():
            nl_tok = count_tokens(nl, tok_fn)
            pidgin_tok = count_tokens(pidgin, tok_fn)
            ratio = round(nl_tok / pidgin_tok, 4) if pidgin_tok > 0 else None

            rows.append({
                "id":               row["id"],
                "tier":             row["tier"],
                "setting":          row.get("setting", ""),
                "entity_count":     row.get("entity_count", ""),
                "reviewed":         row.get("reviewed", ""),
                "tokenizer":        tok_name,
                "nl_tokens":        nl_tok,
                "pidgin_tokens":    pidgin_tok,
                "compression_ratio": ratio,
                "nl_chars":         nl_chars,
                "pidgin_chars":     pidgin_chars,
                "char_ratio":       char_ratio,
            })

            done += 1
            if verbose and done % 50 == 0:
                print(f"  {done}/{total} counts complete...")

    return pd.DataFrame(rows)


# ── SUMMARY STATS ─────────────────────────────────────────────────────────────

def compute_summary(results_df):
    """Produce summary statistics grouped by tokenizer and tier."""
    valid = results_df[results_df["compression_ratio"].notna() &
                       (results_df["nl_tokens"] > 0) &
                       (results_df["pidgin_tokens"] > 0)]

    # Overall stats per tokenizer
    overall = (
        valid.groupby("tokenizer")["compression_ratio"]
        .agg(["mean", "median", "min", "max", "std", "count"])
        .round(4)
        .reset_index()
    )
    overall.columns = ["tokenizer", "mean_ratio", "median_ratio",
                        "min_ratio", "max_ratio", "std_ratio", "n_cases"]

    # Stats per tokenizer per tier
    by_tier = (
        valid.groupby(["tokenizer", "tier"])["compression_ratio"]
        .agg(["mean", "median", "std", "count"])
        .round(4)
        .reset_index()
    )
    by_tier.columns = ["tokenizer", "tier", "mean_ratio",
                        "median_ratio", "std_ratio", "n_cases"]

    # Character-level compression (tokenizer-independent)
    char_stats = (
        valid.drop_duplicates("id")[["id", "tier", "char_ratio"]]
        .groupby("tier")["char_ratio"]
        .agg(["mean", "median", "min", "max"])
        .round(4)
        .reset_index()
    )

    return overall, by_tier, char_stats


# ── VISUALIZATIONS ────────────────────────────────────────────────────────────

def make_plots(results_df, output_dir):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.ticker as mticker
        import seaborn as sns
    except ImportError:
        print("  matplotlib/seaborn not available — skipping plots")
        return

    plots_dir = output_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    valid = results_df[results_df["compression_ratio"].notna() &
                       (results_df["nl_tokens"] > 0) &
                       (results_df["pidgin_tokens"] > 0)].copy()
    valid["tier_label"] = valid["tier"].map({1: "Tier 1\nSimple",
                                              2: "Tier 2\nMedium",
                                              3: "Tier 3\nComplex"})

    palette = {
        "Tier 1\nSimple":  "#4C9BE8",
        "Tier 2\nMedium":  "#2E7D32",
        "Tier 3\nComplex": "#C62828",
    }

    # ── Plot 1: Box plot — compression ratio by tier ──────────────────────────
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(data=valid, x="tier_label", y="compression_ratio",
                palette=palette, width=0.5, ax=ax)
    ax.axhline(1.0, color="gray", linestyle="--", linewidth=1, label="No compression (1.0x)")
    ax.set_title("LLM Pidgin Compression Ratio by Content Complexity Tier",
                 fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Complexity Tier", fontsize=11)
    ax.set_ylabel("Compression Ratio (NL tokens / Pidgin tokens)", fontsize=11)
    ax.legend(fontsize=9)
    plt.tight_layout()
    fig.savefig(plots_dir / "01_compression_by_tier.png", dpi=150)
    plt.close()

    # ── Plot 2: Heatmap — mean ratio per tokenizer per tier ───────────────────
    pivot = (
        valid.groupby(["tokenizer", "tier"])["compression_ratio"]
        .mean()
        .unstack("tier")
        .round(2)
    )
    pivot.columns = [f"Tier {c}" for c in pivot.columns]
    if not pivot.empty:
        fig, ax = plt.subplots(figsize=(7, max(4, len(pivot) * 0.55 + 1)))
        sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGn",
                    linewidths=0.5, ax=ax, cbar_kws={"label": "Mean Compression Ratio"})
        ax.set_title("Mean Compression Ratio per Tokenizer × Tier",
                     fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Complexity Tier", fontsize=10)
        ax.set_ylabel("Tokenizer", fontsize=10)
        plt.tight_layout()
        fig.savefig(plots_dir / "02_heatmap_tokenizer_tier.png", dpi=150)
        plt.close()

    # ── Plot 3: Scatter — NL vs Pidgin token counts ───────────────────────────
    # Use first available tokenizer for scatter
    first_tok = valid["tokenizer"].iloc[0] if len(valid) > 0 else None
    if first_tok:
        scatter_data = valid[valid["tokenizer"] == first_tok]
        fig, ax = plt.subplots(figsize=(7, 6))
        colors = scatter_data["tier"].map({1: "#4C9BE8", 2: "#2E7D32", 3: "#C62828"})
        ax.scatter(scatter_data["nl_tokens"], scatter_data["pidgin_tokens"],
                   c=colors, alpha=0.75, s=60, edgecolors="white", linewidth=0.5)
        max_val = max(scatter_data["nl_tokens"].max(), scatter_data["pidgin_tokens"].max()) * 1.05
        ax.plot([0, max_val], [0, max_val], "k--", linewidth=1, alpha=0.4, label="1:1 (no compression)")
        # Legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor="#4C9BE8", label="Tier 1 — Simple"),
            Patch(facecolor="#2E7D32", label="Tier 2 — Medium"),
            Patch(facecolor="#C62828", label="Tier 3 — Complex"),
        ]
        ax.legend(handles=legend_elements, fontsize=9)
        ax.set_xlim(0, max_val)
        ax.set_ylim(0, max_val)
        ax.set_title(f"NL vs Pidgin Token Counts ({first_tok})",
                     fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Natural Language Token Count", fontsize=11)
        ax.set_ylabel("LLM Pidgin Token Count", fontsize=11)
        plt.tight_layout()
        fig.savefig(plots_dir / "03_scatter_nl_vs_pidgin.png", dpi=150)
        plt.close()

    # ── Plot 4: Bar chart — mean ratio per tokenizer (overall) ───────────────
    overall_means = (
        valid.groupby("tokenizer")["compression_ratio"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )
    if not overall_means.empty:
        fig, ax = plt.subplots(figsize=(max(8, len(overall_means) * 0.8), 5))
        bars = ax.bar(overall_means["tokenizer"], overall_means["compression_ratio"],
                      color="#4C9BE8", edgecolor="white", linewidth=0.5)
        ax.axhline(1.0, color="gray", linestyle="--", linewidth=1)
        ax.set_title("Mean Compression Ratio by Tokenizer (All Tiers)",
                     fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Tokenizer", fontsize=10)
        ax.set_ylabel("Mean Compression Ratio", fontsize=10)
        plt.xticks(rotation=35, ha="right", fontsize=9)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.02,
                    f"{bar.get_height():.2f}x",
                    ha="center", va="bottom", fontsize=8)
        plt.tight_layout()
        fig.savefig(plots_dir / "04_mean_ratio_by_tokenizer.png", dpi=150)
        plt.close()

    print(f"  Plots saved to {plots_dir}/")


# ── REPORT ────────────────────────────────────────────────────────────────────

def print_report(overall, by_tier, char_stats, skipped):
    print("\n" + "═" * 60)
    print("  LLM PIDGIN — TOKEN COMPRESSION RESULTS")
    print("═" * 60)

    print("\n── Overall Compression Ratio by Tokenizer ──\n")
    print(f"  {'Tokenizer':<22} {'Mean':>7} {'Median':>8} {'Min':>7} {'Max':>7} {'N':>5}")
    print("  " + "-" * 55)
    for _, r in overall.iterrows():
        print(f"  {r['tokenizer']:<22} {r['mean_ratio']:>7.2f}x {r['median_ratio']:>7.2f}x "
              f"{r['min_ratio']:>6.2f}x {r['max_ratio']:>6.2f}x {int(r['n_cases']):>5}")

    print("\n── Mean Compression Ratio by Tier ──\n")
    for tok in by_tier["tokenizer"].unique():
        tok_data = by_tier[by_tier["tokenizer"] == tok]
        tier_str = "  ".join([f"T{int(r['tier'])}: {r['mean_ratio']:.2f}x"
                               for _, r in tok_data.iterrows()])
        print(f"  {tok:<22} {tier_str}")

    print("\n── Character-Level Compression by Tier ──\n")
    print(f"  {'Tier':<10} {'Mean':>7} {'Median':>8} {'Min':>7} {'Max':>7}")
    print("  " + "-" * 42)
    for _, r in char_stats.iterrows():
        print(f"  Tier {int(r['tier']):<5} {r['mean']:>7.2f}x {r['median']:>7.2f}x "
              f"{r['min']:>6.2f}x {r['max']:>6.2f}x")

    if skipped:
        print(f"\n── Skipped Tokenizers ({len(skipped)}) ──")
        for name, reason in skipped.items():
            print(f"  ✗ {name}: {reason[:70]}")

    print("\n" + "═" * 60 + "\n")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LLM Pidgin Token Compression Benchmark")
    parser.add_argument("--input",  default="test_cases.csv",  help="Path to test cases CSV")
    parser.add_argument("--output", default="results",          help="Output directory")
    parser.add_argument("--no-plots", action="store_true",      help="Skip plot generation")
    parser.add_argument("--only",   nargs="+",                  help="Run only these tokenizers")
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    # ── Load test cases ───────────────────────────────────────────────────────
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)

    df = pd.read_csv(input_path)
    required = {"id", "tier", "nl_text", "pidgin_text"}
    missing = required - set(df.columns)
    if missing:
        print(f"Error: CSV missing required columns: {missing}")
        sys.exit(1)

    # Filter to reviewed only (if column exists and has values)
    if "reviewed" in df.columns:
        unreviewed = df[df["reviewed"] != True].shape[0]
        if unreviewed > 0:
            print(f"Warning: {unreviewed} cases not marked as reviewed. Including anyway.")

    print(f"\nLoaded {len(df)} test cases from {input_path}")
    print(f"Tier distribution: { df['tier'].value_counts().sort_index().to_dict() }")

    # ── Load tokenizers ───────────────────────────────────────────────────────
    print("\nLoading tokenizers...")
    all_tokenizers, skipped = build_tokenizers(verbose=True)

    if args.only:
        all_tokenizers = {k: v for k, v in all_tokenizers.items() if k in args.only}

    if not all_tokenizers:
        print("Error: no tokenizers loaded. Install tiktoken and/or transformers.")
        sys.exit(1)

    print(f"\nLoaded {len(all_tokenizers)} tokenizers. Skipped {len(skipped)}.")

    # ── Run counts ────────────────────────────────────────────────────────────
    print(f"\nCounting tokens ({len(df)} cases × {len(all_tokenizers)} tokenizers = "
          f"{len(df) * len(all_tokenizers)} operations)...\n")

    results = run_counts(df, all_tokenizers, verbose=True)

    # ── Save raw results ──────────────────────────────────────────────────────
    raw_path = output_path / "raw_counts.csv"
    results.to_csv(raw_path, index=False)
    print(f"\nRaw counts saved to {raw_path}")

    # ── Summary stats ─────────────────────────────────────────────────────────
    overall, by_tier, char_stats = compute_summary(results)

    overall.to_csv(output_path / "summary_overall.csv", index=False)
    by_tier.to_csv(output_path / "summary_by_tier.csv", index=False)
    char_stats.to_csv(output_path / "summary_char.csv", index=False)

    # Save compression ratios wide format (one row per case, one col per tokenizer)
    ratio_wide = results.pivot_table(
        index=["id", "tier", "setting"],
        columns="tokenizer",
        values="compression_ratio"
    ).reset_index()
    ratio_wide.to_csv(output_path / "compression_ratios_wide.csv", index=False)

    # Save skipped tokenizers log
    with open(output_path / "skipped_tokenizers.json", "w") as f:
        json.dump(skipped, f, indent=2)

    # ── Plots ─────────────────────────────────────────────────────────────────
    if not args.no_plots:
        print("\nGenerating plots...")
        make_plots(results, output_path)

    # ── Print report ──────────────────────────────────────────────────────────
    print_report(overall, by_tier, char_stats, skipped)
    print(f"All results saved to {output_path}/")


if __name__ == "__main__":
    main()
