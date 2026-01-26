# CameleonCV 🦎

**Document-aware CV transformation using LLaMA 3 (8B) + LoRA fine-tuning.**

Transform your CV into 5 distinct writing styles while preserving every fact, metric, and achievement. One resume, multiple voices — all ATS-compliant.

> ⚠️ **Work in Progress** — Currently at ~35% completion

🌐 **Live:** [cameleonai.eu](https://cameleonai.eu)

---

## The Problem

Job seekers face a dilemma: a CV optimized for a corporate finance role sounds wrong for a startup, and vice versa. Manually rewriting for each application is time-consuming and error-prone.

Existing AI writing tools either:
- Change facts (hallucination)
- Apply superficial word swaps (no real style shift)
- Ignore context (job requirements, section type)

## The Solution

CameleonCV separates **what to say** from **how to say it**:

| Component | Responsibility |
|-----------|----------------|
| **LoRA Adapters** | Learn style transformation patterns |
| **Prompt Logic** | Handle context, constraints, and formatting at runtime |

This separation means the model focuses purely on stylistic transformation while external controls ensure factual preservation.

---

## Five Styles

| Style | Intent | Best For |
|-------|--------|----------|
| **Professional** | Polished, business-appropriate language | Corporate roles, traditional industries |
| **Academic** | Scholarly precision with methodological rigor | Research positions, universities |
| **Confident** | Bold, assertive statements | Leadership roles, competitive fields |
| **Concise** | Maximum information density | Technical roles, busy recruiters |
| **Playful** | Personality with functional icons | Startups, creative agencies |

Each style has operational definitions with explicit linguistic markers, anti-patterns, and boundary conditions. See [docs/style-definitions.md](docs/style-definitions.md) for details.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      USER INPUT                         │
│  • Original CV section                                  │
│  • Job posting excerpt                                  │
│  • Target style selection                               │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   PROMPT ASSEMBLY                       │
│  • Section-specific instructions                        │
│  • Factual preservation constraints                     │
│  • Style-specific guidelines                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              LLaMA 3 (8B) + LoRA ADAPTER                │
│                                                         │
│  Base Model: General language understanding             │
│  LoRA Layer: Style-specific transformation patterns     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│                   TRANSFORMED OUTPUT                    │
│  • Same facts, different voice                          │
│  • ATS-compliant formatting                             │
│  • Ready for CV submission                              │
└─────────────────────────────────────────────────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed design rationale.

---

## Dataset

### Composition

| Dimension | Count |
|-----------|-------|
| Seed examples | 210 |
| Styles | 5 |
| Total transformations | 1,050 |
| Section types | 5 (summary, experience, education, skills, projects) |
| Role categories | 5 (technical, business, creative, academic, operations) |
| Seniority levels | 4 (entry, mid, senior, executive) |

### Quality Controls

- **Factual validation:** Entity extraction comparison between original and transformed
- **Style validation:** LLM-based scoring against operational definitions
- **Human review:** Spot-checking for edge cases and systematic issues

See [docs/dataset-schema.md](docs/dataset-schema.md) for the full schema specification.

---

## Evaluation Framework

Three-dimensional assessment:

| Dimension | What It Measures | Method |
|-----------|------------------|--------|
| **Style Fidelity** | Does output match target style? | LLM scoring against rubrics |
| **Factual Consistency** | Are all facts preserved? | Entity extraction + comparison |
| **Quality/ATS** | Is it professional and parseable? | Automated + manual review |

### Comparison Strategy

| Model | Purpose |
|-------|---------|
| Base LLaMA 3 (zero-shot) | Baseline without training |
| Base LLaMA 3 (few-shot) | Baseline with examples in prompt |
| LoRA-adapted model | Our fine-tuned approach |

---

## Progress

- [x] Operational style definitions
- [x] Dataset schema design
- [x] 210 seed examples created
- [ ] Style transformations (~35% complete)
- [ ] LoRA fine-tuning
- [ ] Evaluation framework implementation
- [ ] Interactive demo

---

## Technical Stack

| Component | Technology |
|-----------|------------|
| Base model | LLaMA 3 (8B) |
| Fine-tuning | LoRA via Unsloth |
| Quantization | 4-bit (QLoRA) |
| Training environment | Google Colab Pro (A100) |
| Landing page | React + Vite + Vercel |
| Data generation | Synthetic via DeepSeek-R1 |

---

## Project Structure

```
CameleonCV/
├── README.md
├── docs/
│   ├── style-definitions.md    # Operational definitions for 5 styles
│   ├── dataset-schema.md       # JSONL format and validation rules
│   └── architecture.md         # Design decisions and rationale
├── data/
│   ├── examples/               # Sample data (not full dataset)
│   └── schema/                 # JSON schema files
├── landing-page/
│   └── App.jsx                 # React landing page
├── training/                   # (Coming soon)
│   ├── config/
│   └── scripts/
└── evaluation/                 # (Coming soon)
    ├── prompts/
    └── results/
```

---

## Why This Approach?

### Why LoRA instead of full fine-tuning?
- **Efficiency:** ~50-100MB adapter vs 16GB+ full model
- **Composability:** Can swap adapters for different styles
- **Accessibility:** Trainable on consumer hardware (Colab)

### Why synthetic data?
- **Ethics:** No privacy concerns from real CVs
- **Control:** Exact distribution across categories
- **Quality:** Each example validated for factual preservation

### Why section-level instead of full CVs?
- **Cleaner signal:** One section → one style → one output
- **Flexibility:** Users can mix styles per section
- **Data efficiency:** 1,000 examples vs 5,000+ needed for full CVs

---

## Limitations

- **English only** (for now)
- **Text-based** — no formatting/layout transformation
- **Style, not content** — won't add missing information
- **Requires quality input** — garbage in, stylized garbage out

---

## Author

Built by [Georgie](https://linkedin.com/in/georgieslab) as a portfolio project demonstrating ML engineering capabilities.

This project is designed to be:
- **Technically defensible** — Real architectural decisions, not just API wrappers
- **Interview-ready** — Can explain every tradeoff
- **Ethically sound** — Synthetic data, no personal information

---

## License

MIT License — See [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Unsloth](https://github.com/unslothai/unsloth) for efficient LoRA training
- [Anthropic](https://anthropic.com) for Claude (dataset design assistance)
- [DeepSeek](https://deepseek.com) for R1 model (data generation)
