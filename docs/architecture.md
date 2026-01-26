# Architecture

This document explains the design decisions behind CameleonCV, including why certain approaches were chosen over alternatives.

---

## Core Design Principle

**Separate learned behavior from runtime orchestration.**

| Component | Handles | Why |
|-----------|---------|-----|
| **LoRA Adapters** | Style transformation patterns | Learned from data, captures "how to say it" |
| **Prompt Logic** | Context injection, constraints, formatting | Flexible at runtime, captures "what to say" |

This separation provides:
- **Cleaner training signal** — Model focuses on one task
- **Runtime flexibility** — Can change context without retraining
- **Easier debugging** — Know where to look when something fails

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│  • Upload CV section                                            │
│  • Provide job posting                                          │
│  • Select target style                                          │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROMPT ASSEMBLY LAYER                      │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │   Section   │  │    Style    │  │      Constraints        │ │
│  │   Template  │  │ Instructions│  │  (factual preservation) │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
│                                                                 │
│  Output: Complete prompt with context + instructions            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        MODEL LAYER                              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    LLaMA 3 (8B)                           │ │
│  │                    Base Model                              │ │
│  │                                                           │ │
│  │   General language understanding, grammar, coherence      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                            │                                    │
│                            ▼                                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                  LoRA Adapter                             │ │
│  │              (Style-Specific)                             │ │
│  │                                                           │ │
│  │   Learned: Vocabulary preferences, sentence patterns,     │ │
│  │            tone markers, structural tendencies            │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     POST-PROCESSING                             │
│                                                                 │
│  • Extract generated section                                    │
│  • Validate factual consistency (optional)                      │
│  • Format for output                                            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TRANSFORMED OUTPUT                         │
│                                                                 │
│  Same facts, different voice, ready for CV                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why LoRA?

### What is LoRA?

**Low-Rank Adaptation** freezes the base model and injects small trainable matrices into attention layers. Instead of updating billions of parameters, we train millions.

```
Original: W (frozen, 4096 × 4096)
LoRA:     W + BA where B (4096 × r), A (r × 4096), r = 16
Trainable parameters: 2 × 4096 × 16 = 131,072 vs 16,777,216
```

### Why LoRA over alternatives?

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Full fine-tuning** | Maximum capacity | Requires 80GB+ VRAM, catastrophic forgetting risk | ❌ Overkill |
| **Prompt tuning** | Very lightweight | Limited expressiveness | ❌ Too weak |
| **LoRA** | Efficient, composable, accessible | Slightly less capacity than full fine-tuning | ✅ Right fit |
| **QLoRA** | LoRA + 4-bit quantization | Minimal quality loss | ✅ Using this |

### LoRA Configuration

```python
lora_config = {
    "r": 16,                    # Rank (capacity)
    "lora_alpha": 32,           # Scaling factor
    "lora_dropout": 0.05,       # Regularization
    "target_modules": [
        "q_proj", "k_proj",     # Attention query/key
        "v_proj", "o_proj",     # Attention value/output
        "gate_proj", "up_proj", # MLP layers
        "down_proj"
    ]
}
```

**Why these choices:**
- **r=16**: Sufficient for style transformation; higher values showed diminishing returns in experiments
- **alpha=32**: 2× rank is standard; provides good gradient scaling
- **dropout=0.05**: Light regularization; dataset is clean so heavy regularization unnecessary
- **All attention + MLP**: Style affects both attention patterns (what to focus on) and MLP (vocabulary/phrasing)

---

## Why Section-Level Granularity?

### Alternative: Full CV Transformation

Transform entire CVs at once.

**Problems:**
- Requires more training data (1,500+ full CVs vs 1,000 sections)
- Harder to evaluate (which section caused a failure?)
- Less flexible (can't mix styles per section)
- Longer sequences (memory/compute cost)

### Our Approach: Section-Level

Transform one section at a time.

**Benefits:**
- **Cleaner training signal**: One input → one output → one style
- **Composability**: User can apply different styles to different sections
- **Data efficiency**: 1,000 examples is sufficient
- **Easier evaluation**: Can isolate exactly what went wrong

### Section Types

| Section | Transformation Challenge |
|---------|-------------------------|
| **Summary** | Dense, must sound cohesive |
| **Experience** | Structured, metrics-heavy |
| **Education** | Relatively fixed format |
| **Skills** | List format, minimal transformation |
| **Projects** | Narrative + technical balance |

Each section type has different hallucination risks and style opportunities, which is why section-specific prompts are used during data generation.

---

## Why Synthetic Data?

### Alternative: Real CV Dataset

Scrape or collect real CVs, transform them.

**Problems:**
- **Privacy**: Real CVs contain PII
- **Consent**: People didn't agree to ML training
- **Quality**: Real CVs are messy, inconsistent
- **Distribution**: Hard to ensure balanced coverage

### Our Approach: Synthetic Generation

Generate realistic but fictional CV content using LLMs.

**Benefits:**
- **Ethical**: No privacy concerns
- **Controlled**: Exact distribution across categories
- **Clean**: Consistent quality and format
- **Transparent**: Fully documented methodology

### Generation Pipeline

```
1. Define seed parameters
   - Section type: summary
   - Role category: technical
   - Seniority: entry-level
   
2. Generate neutral CV section
   - LLM creates realistic content
   - No style applied yet
   
3. Generate matching job posting
   - Plausible next-step role
   - Relevant requirements
   
4. Apply style transformations
   - One transformation per style
   - Strict factual preservation
   
5. Validate outputs
   - Automated schema checks
   - LLM-based quality scoring
   - Manual review for edge cases
```

---

## Prompt vs. Model: Responsibility Split

### What the Prompt Handles (Runtime)

| Responsibility | Why Prompt? |
|----------------|-------------|
| Original CV content | Different every time |
| Job posting context | Different every time |
| Section type instructions | Could change without retraining |
| Factual constraints | Explicit rules > learned behavior |
| Output format | Explicit specification |

### What the Model Learns (Training)

| Responsibility | Why Learned? |
|----------------|--------------|
| Style vocabulary | Subtle, hard to specify |
| Sentence rhythm | Pattern recognition |
| Tone consistency | Holistic, not rule-based |
| Style-appropriate structure | Emergent from examples |

### Why This Split?

**Factual constraints in prompt, not learned:**
- Rules like "don't hallucinate" are better explicit than implicit
- Learned constraints can be forgotten or overridden
- Prompt constraints are auditable and adjustable

**Style patterns learned, not prompted:**
- Style is too nuanced for rule-based specification
- Hundreds of examples teach patterns better than instructions
- Learned style is more consistent than prompted style

---

## Training-Inference Parity

### The Principle

The model should see the same input format during training as it will during inference.

### Implementation

**Training input:**
```
### TASK
Rewrite the following CV section according to the specified style and constraints.

### ORIGINAL CV SECTION
{original_section}

### TARGET JOB CONTEXT
{job_posting_excerpt}          ← Included even though LoRA ignores it

### INSTRUCTIONS
{instructions}

### REWRITTEN SECTION
{target_output}                 ← Model learns to generate this
```

**Inference input:**
```
### TASK
Rewrite the following CV section according to the specified style and constraints.

### ORIGINAL CV SECTION
{user_cv_section}

### TARGET JOB CONTEXT
{user_job_posting}              ← Same format as training

### INSTRUCTIONS
{style_instructions}

### REWRITTEN SECTION
                                ← Model generates from here
```

### Why Include Job Posting in Training?

The LoRA adapter handles style, not job-relevance. So why include job postings?

1. **Format consistency**: Model learns to produce output regardless of job context length
2. **Future-proofing**: Might add job-aware features later
3. **Realistic context**: Real usage will include job postings

---

## Evaluation Architecture

### Three-Dimensional Assessment

```
                    ┌─────────────────┐
                    │   TRANSFORMED   │
                    │     OUTPUT      │
                    └─────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   STYLE     │ │  FACTUAL    │ │  QUALITY    │
    │  FIDELITY   │ │ CONSISTENCY │ │  / ATS      │
    └─────────────┘ └─────────────┘ └─────────────┘
            │               │               │
            ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ LLM Scoring │ │   Entity    │ │  Automated  │
    │  vs Rubric  │ │ Extraction  │ │   Checks    │
    └─────────────┘ └─────────────┘ └─────────────┘
```

### Comparison Strategy

| Model | Configuration | Purpose |
|-------|---------------|---------|
| **Baseline 1** | LLaMA 3 8B, zero-shot | What can the model do without training? |
| **Baseline 2** | LLaMA 3 8B, 5-shot | What can few-shot prompting achieve? |
| **Ours** | LLaMA 3 8B + LoRA | What does fine-tuning add? |

### Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Style fidelity (LoRA vs zero-shot) | +15% | Must show meaningful improvement |
| Factual consistency | >95% | Non-negotiable for real-world use |
| Latency | <3s per section | Usable in interactive demo |

---

## Limitations and Tradeoffs

### What This System Can't Do

| Limitation | Why |
|------------|-----|
| **Add missing content** | Model transforms, doesn't create |
| **Fix bad input** | Garbage in → stylized garbage out |
| **Handle non-English** | Training data is English only |
| **Transform formatting** | Text-only, no layout/design |
| **Guarantee ATS parsing** | Can optimize, not guarantee |

### Tradeoffs Made

| Decision | Tradeoff | Rationale |
|----------|----------|-----------|
| LoRA over full fine-tuning | Slightly less capacity | Accessibility > marginal quality |
| Synthetic over real data | Less "real-world" variety | Ethics > data diversity |
| Section-level granularity | More user interaction | Flexibility > convenience |
| 5 styles only | Limited options | Depth > breadth |

---

## Future Extensions

### Potential Improvements

| Extension | Complexity | Value |
|-----------|------------|-------|
| Multi-language support | High | Opens new markets |
| More styles | Low | Easy to add adapters |
| Full CV generation | Medium | Higher user convenience |
| Job-aware optimization | Medium | Better relevance |
| Real-time feedback | Medium | Better UX |

### Architecture Support

The current design supports these extensions:
- **Multi-language**: Train separate LoRA per language
- **More styles**: Add more adapters (composable)
- **Job-aware**: Already includes job context in prompt
- **Real-time**: Inference is fast enough (<3s)

---

## Technical Decisions Summary

| Decision | Chosen | Alternatives Considered |
|----------|--------|------------------------|
| Base model | LLaMA 3 8B | Mistral 7B, LLaMA 2, Phi-2 |
| Fine-tuning method | QLoRA | Full FT, prompt tuning, adapters |
| Training framework | Unsloth | Axolotl, HF PEFT, LLaMA-Factory |
| Quantization | 4-bit NF4 | 8-bit, no quantization |
| Training compute | Colab Pro A100 | Local GPU, cloud instances |
| Data format | JSONL | CSV, Parquet, HF datasets |
| Granularity | Section-level | Full CV, sentence-level |
| Data source | Synthetic | Real CVs, templates |

---

## References

- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [QLoRA: Efficient Finetuning of Quantized LLMs](https://arxiv.org/abs/2305.14314)
- [Unsloth: Fast LLM Fine-tuning](https://github.com/unslothai/unsloth)
- [LLaMA 3 Technical Report](https://ai.meta.com/blog/meta-llama-3/)
