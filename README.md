# LLM-Pidgin

An experiment in developing a token-efficient shorthand for LLMs — a "pidgin" dialect that preserves nuance and context while reducing token cost by 30–50%.

## Goal

Design and evaluate a compressed language register (LLM-Pidgin) that allows LLMs to communicate internally or across calls with fewer tokens, without losing semantic fidelity.

## Structure

```
prompts/           # Generation and decoding prompt templates
data/
  raw/             # Original input texts
  processed/       # Cleaned/formatted inputs
  outputs/         # Raw model outputs
experiments/       # Experiment configs and run logs
scripts/           # Evaluation and utility scripts
results/           # Scored outputs and analysis
notebooks/         # Exploratory analysis
docs/              # Design notes, pidgin grammar rules
```

## Quick Start

1. Add input texts to `data/raw/`.
2. Use `prompts/gpt4_generation_prompt.md` to generate pidgin versions.
3. Evaluate with `scripts/evaluate_fidelity.py`:
   ```bash
   python scripts/evaluate_fidelity.py results/run_001.jsonl
   ```
4. Log findings in `experiments/` using the template.
