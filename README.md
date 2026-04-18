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

```bash
pip install -r requirements.txt
```

1. Use `prompts/gpt4_generation_prompt.md` in a GPT-4.1 session to generate test cases IDs 11–50 as CSV rows.
2. Save the seed + generated cases as `data/raw/test_cases.csv` (columns: `id, tier, setting, entity_count, nl_text, pidgin_text, reviewed, notes`).
3. Run the token compression benchmark:
   ```bash
   python scripts/token_counter.py --input data/raw/test_cases.csv --output results/
   ```
4. Results land in `results/`: raw counts, summary CSVs, and plots.
5. Log findings in `experiments/` using `experiments/experiment_template.md`.
