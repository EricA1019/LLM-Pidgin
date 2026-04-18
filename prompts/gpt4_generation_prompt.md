# GPT-4.1 Generation Prompt
# Use this prompt to generate the remaining 40 test cases for the benchmark.
# Run this in a single GPT-4.1 session to maintain consistency.

---

SYSTEM:
You are assisting with a research benchmark for a notation system called LLM Pidgin.
Your job is to generate natural language character/scene descriptions and convert
each one to LLM Pidgin notation.

## LLM Pidgin v0.1 Quick Reference

STRUCTURE
  {}    entity scope          {Alex brave+quiet}
  []    context/scene         [night][warzone]
  ()    role qualifier        Father(Jose)
  ""    natural language      Jose="army ranger"
  ::    namespace             Background::  Goal::
  //    human comment (strip)

STATE
  =     assignment            trust=low
  !=    negation/excluded     Alex != family
  ~=    approximate           strength~=veteran
  ?=    uncertain             motive?=revenge
  !x    not prefix            !loyal  !alive

CAUSATION
  ->    causes/leads to       Jose=dead -> trust=low
  <-    caused by             grief <- Father=dead
  <->   mutual/bidirectional  rivals <-> allies
  =>    strongly implies      ranger => combat_trained
  ~>    loosely leads to      grief ~> isolation

LOGIC
  +     and also (additive)   brave+quiet+scarred
  &     explicit AND          alive & present
  |     or/alternatively      revenge | justice
  *     recurring pattern     *nightmares

PRIORITY
  >     dominates             revenge > grief
  >>    strongly dominates    survival >> honor

ANCHORS
  @     time/place            @past  @city_gates
  @+    future state          @+Alex=general
  @-    past state (no longer true)  @-Jose=alive
  $x    variable placeholder  $enemy

META
  !     emphasis/critical     !secret  !core_trait
  #     category tag          #military #loss
  ?     uncertainty modifier  ?loyal  ?sane
  ...   implied continuation  history=long...

## Examples

Natural language:
"Alex's father Jose was an army ranger who died in combat.
Alex never recovered and struggles to trust people as a result."

LLM Pidgin:
{Background::Father(Jose)=dead+Jose="army ranger"->died_in_war}
{Personality::trust=low->Background::Father(Jose)}
{Emotion::grief=*latent}

---

USER PROMPT (send this after the system prompt):

Generate test cases IDs 11 through 50 for the LLM Pidgin compression benchmark.

For each case, produce:
1. A natural language description (prose, no bullet points)
2. The equivalent LLM Pidgin encoding

Follow this distribution exactly:
- IDs 11-17: Tier 1 (Simple) — single entity, basic attributes, no causal chains
- IDs 18-31: Tier 2 (Medium) — 1-2 entities, at least one relationship, one causal chain
- IDs 32-46: Tier 3 (Complex) — 3+ entities, multiple causal chains, cross-referenced relationships
- IDs 47-48: Tier 1
- ID 49: Tier 2
- ID 50: Tier 3

Variation requirements across all 40 cases:
- Use at least 6 different settings: military, domestic, fantasy, sci-fi, political, contemporary, historical
- Include at least 6 cases with scene/environmental context using [] blocks
- Include at least 6 cases with temporal anchors (@, @-, @+)
- Include at least 5 cases with uncertainty (?=, ?)
- Include at least 5 cases with recurring patterns (*)
- Include at least 4 cases with conflicting goals (>> or >)
- Do NOT repeat any setting/character combination from the 10 seed cases already provided

Output format — output ONLY valid CSV rows, no markdown, no explanations.
Each row must follow this exact format:
id,tier,setting,entity_count,nl_text,pidgin_text,reviewed,notes

Rules:
- Wrap nl_text and pidgin_text in double quotes
- If the text contains double quotes, escape them as ""
- reviewed column = FALSE for all generated cases
- notes column = "generated"
- entity_count = number of named entities in the case
- setting = one word (military/domestic/fantasy/sci-fi/political/contemporary/historical/medical/legal)

Begin output now with row id 11.
