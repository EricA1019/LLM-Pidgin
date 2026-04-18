# Experiment Design

## Research Question

Can a structured symbolic shorthand (LLM Pidgin) reduce token consumption in LLM prompts and context windows by 30–50% without measurable loss of semantic fidelity?

## Hypothesis

LLM Pidgin encoding will achieve:
- ≥1.3x token compression on Tier 2 and Tier 3 cases across GPT-series tokenizers
- ≥1.5x character-level compression across all tiers
- Compression gains increase with content complexity (Tier 1 < Tier 2 < Tier 3) at the character level
- Token-level gains will be smaller than character-level gains due to subword tokenizer behavior on novel symbols

## Benchmark Design

### Test Set

- **50 total cases** (10 seed + 40 GPT-4.1 generated)
- Distributed across 3 complexity tiers (see `docs/pidgin_v01_spec.md`)
- Covers ≥6 settings: military, domestic, fantasy, sci-fi, political, contemporary, historical
- CSV schema: `id, tier, setting, entity_count, nl_text, pidgin_text, reviewed, notes`

### Tokenizers Evaluated

| Tokenizer | Model Family | Auth Required |
|-----------|-------------|---------------|
| `gpt4_cl100k` | GPT-4 / GPT-3.5 | No |
| `gpt4o_o200k` | GPT-4o | No |
| `mistral_7b` | Mistral 7B | No |
| `mistral_nemo` | Mistral Nemo | No |
| `qwen2_7b` | Qwen 2 | No |
| `phi3_mini` | Phi-3 Mini | No |
| `phi3_medium` | Phi-3 Medium | No |
| `deepseek_v2` | DeepSeek V2 | No |
| `command_r` | Command R | No |
| `gemma2_9b` | Gemma 2 | HF account |
| `llama3_8b` | Llama 3 | HF account |
| `llama3_70b` | Llama 3 70B | HF account |

### Primary Metric

**Compression Ratio** = `nl_tokens / pidgin_tokens`

A ratio >1.0 means the pidgin version uses fewer tokens.

### Secondary Metrics

- Character compression ratio (`nl_chars / pidgin_chars`)
- Ratio variance across tiers (does complexity help?)
- Tokenizer-to-tokenizer variance (is Pidgin tokenizer-agnostic?)

## Workflow

```
prompts/gpt4_generation_prompt.md
        │
        ▼ (GPT-4.1 session)
data/raw/test_cases.csv
        │
        ▼
python scripts/token_counter.py --input data/raw/test_cases.csv --output results/
        │
        ├── results/raw_counts.csv
        ├── results/summary_overall.csv
        ├── results/summary_by_tier.csv
        ├── results/compression_ratios_wide.csv
        └── results/plots/
```

## Success Criteria

| Metric | Target |
|--------|--------|
| Mean token compression (Tier 2+, GPT tokenizers) | ≥1.3x |
| Mean character compression (all tiers) | ≥1.5x |
| Cases where pidgin HURTS compression (ratio <1.0) | <20% |
| Tier 3 > Tier 1 compression | Must hold for char ratio |

## Next Steps

- [ ] Generate cases 11–50 using `prompts/gpt4_generation_prompt.md`
- [ ] Human review all 50 cases (set `reviewed=TRUE` in CSV)
- [ ] Run full benchmark: `python scripts/token_counter.py`
- [ ] Analyze results, update findings below
- [ ] Iterate on symbol set if compression targets not met

## Findings

*(to be filled in after benchmark run)*
