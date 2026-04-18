# LLM Pidgin v0.1 — Grammar & Symbol Reference

A token-efficient notation for encoding natural language descriptions with preserved nuance, intent, and context.

---

## Core Philosophy

LLM Pidgin is not a lossy compression format. Every symbol carries semantic weight. The goal is to eliminate redundant grammatical scaffolding (articles, copulas, filler prepositions) while making relationships, causation, and uncertainty *more* explicit than prose.

**Design priorities (in order):**
1. Semantic fidelity — no meaning loss
2. Token efficiency — target 30–50% reduction on Tier 2–3 content
3. Human readability — a trained reader should parse it without tooling

---

## Symbol Reference

### Structural Delimiters

| Symbol | Name | Usage | Example |
|--------|------|-------|---------|
| `{}` | Entity scope | Wraps a named entity and its attributes | `{Alex brave+quiet}` |
| `[]` | Context block | Scene, environment, or situational frame | `[night][warzone]` |
| `()` | Role qualifier | Clarifies a role or relationship type | `Father(Jose)` |
| `""` | Natural language | Embed prose where pidgin would lose nuance | `Jose="army ranger"` |
| `::` | Namespace | Separates semantic domain from content | `Background::` `Goal::` `Emotion::` |
| `//` | Human comment | Stripped at parse time, for author notes | `// revisit this` |

### State Operators

| Symbol | Meaning | Example |
|--------|---------|---------|
| `=` | Assignment / is | `trust=low` |
| `!=` | Negation / excluded | `Alex != family` |
| `~=` | Approximate / roughly | `strength~=veteran` |
| `?=` | Uncertain assignment | `motive?=revenge` |
| `!x` | Not prefix | `!loyal` `!alive` |

### Causation & Implication

| Symbol | Meaning | Example |
|--------|---------|---------|
| `->` | Causes / leads to | `Jose=dead -> trust=low` |
| `<-` | Caused by | `grief <- Father=dead` |
| `<->` | Mutual / bidirectional | `rivals <-> allies` |
| `=>` | Strongly implies | `ranger => combat_trained` |
| `~>` | Loosely leads to | `grief ~> isolation` |

### Logic Operators

| Symbol | Meaning | Example |
|--------|---------|---------|
| `+` | And also (additive traits) | `brave+quiet+scarred` |
| `&` | Explicit AND (conditional) | `alive & present` |
| `\|` | Or / alternatively | `revenge \| justice` |
| `*` | Recurring pattern | `*nightmares` |

### Priority & Dominance

| Symbol | Meaning | Example |
|--------|---------|---------|
| `>` | Dominates | `revenge > grief` |
| `>>` | Strongly dominates | `survival >> honor` |

### Temporal & Spatial Anchors

| Symbol | Meaning | Example |
|--------|---------|---------|
| `@` | Current time or place | `@past` `@city_gates` |
| `@+` | Future state | `@+Alex=general` |
| `@-` | Past state (no longer true) | `@-Jose=alive` |

### Meta & Modifiers

| Symbol | Meaning | Example |
|--------|---------|---------|
| `!` | Emphasis / critical | `!secret` `!core_trait` |
| `#` | Category tag | `#military` `#loss` |
| `?` | Uncertainty modifier | `?loyal` `?sane` |
| `$x` | Variable placeholder | `$enemy` |
| `...` | Implied continuation | `history=long...` |

---

## Namespace Conventions

Recommended namespaces for character/scene encoding:

| Namespace | Use |
|-----------|-----|
| `Background::` | History, origin, formative events |
| `Personality::` | Traits, behavioral tendencies |
| `Emotion::` | Affective states, recurring feelings |
| `Goal::` | Motivations, objectives, drives |
| `Relationship::` | Inter-entity connections |
| `Scene::` | Environmental or situational context |
| `Status::` | Current physical/social/political state |

---

## Encoding Example

**Natural language:**
> "Alex's father Jose was an army ranger who died in combat. Alex never recovered and struggles to trust people as a result."

**LLM Pidgin:**
```
{Background::Father(Jose)=dead+Jose="army ranger"->died_in_war}
{Personality::trust=low->Background::Father(Jose)}
{Emotion::grief=*latent}
```

**Token reduction (GPT-4 cl100k):** ~38%

---

## Tier Definitions (Benchmark)

| Tier | Label | Criteria |
|------|-------|----------|
| 1 | Simple | Single entity, basic attributes, no causal chains |
| 2 | Medium | 1–2 entities, at least one relationship, one causal chain |
| 3 | Complex | 3+ entities, multiple causal chains, cross-referenced relationships |

---

## Known Limitations (v0.1)

- Pidgin symbols (especially `{}`, `->`, `::`) tokenize poorly on GPT-series tokenizers — token compression gains are stronger at the character level and for HuggingFace tokenizers with larger vocabularies.
- Tier 1 cases may show <1.0x token compression while still achieving >1.5x character compression.
- Natural language fragments inside `""` reset compression gains for that segment.
- No formal parser exists yet — encoding relies on LLM interpretation.
