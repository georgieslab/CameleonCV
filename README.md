# 🦎 CameleonCV

**AI-powered CV transformation that adapts writing style and job relevance.**

Transform any CV section into 5 distinct writing styles while preserving factual accuracy. Built with LoRA fine-tuning on LLaMA 3 8B.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://cameleonai.eu)
[![Model](https://img.shields.io/badge/model-LLaMA%203%208B-blue)](https://huggingface.co/meta-llama/Meta-Llama-3-8B)
[![Training](https://img.shields.io/badge/training-LoRA-orange)](https://arxiv.org/abs/2106.09685)

---

## 📊 Results

Fine-tuned model vs zero-shot baseline, evaluated using LLM-as-judge methodology:

| Metric | Base Model | Fine-tuned | Improvement |
|--------|-----------|------------|-------------|
| Style Fidelity | 2.48 | 3.64 | **+47%** |
| Factual Consistency | 4.28 | 4.60 | +7% |
| Quality | 3.24 | 3.92 | +21% |
| **Overall** | 3.33 | **4.05** | **+22%** |

**Win Rate:** Fine-tuned model outperforms base model in **76%** of head-to-head comparisons.

<details>
<summary>📈 Results by Style</summary>

| Style | Base Avg | Fine-tuned Avg | Δ |
|-------|----------|----------------|---|
| Professional | 3.2 | 4.1 | +0.9 |
| Academic | 3.1 | 3.9 | +0.8 |
| Confident | 3.4 | 4.2 | +0.8 |
| Concise | 3.5 | 4.3 | +0.8 |
| Playful | 3.4 | 4.0 | +0.6 |

</details>

---

## 🎯 The Problem

Job seekers need to tailor their CVs for different contexts:
- **Startup vs Enterprise** → Different tones expected
- **Technical vs Business roles** → Different emphasis needed
- **Multiple applications** → Time-consuming manual rewrites

CameleonCV solves this by learning distinct writing patterns and applying them consistently while preserving all factual content.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Input                           │
│              (CV Section + Job Posting + Style)             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                 Stage 1: Style Transformation               │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           LoRA-adapted LLaMA 3 (8B)                 │   │
│   │                                                     │   │
│   │   • Pattern learning task                           │   │
│   │   • 5 distinct style transformations                │   │
│   │   • Trained on 1,050 synthetic examples             │   │
│   │   • Preserves factual content                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Stage 2: Job Relevance (Planned)               │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                   Claude API                        │   │
│   │                                                     │   │
│   │   • Reasoning task                                  │   │
│   │   • Matches skills to job requirements              │   │
│   │   • Optimizes keyword alignment                     │   │
│   │   • Preserves style and facts                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      Final Output                           │
│            (Styled + Job-Tailored CV Section)               │
└─────────────────────────────────────────────────────────────┘
```

**Why two stages?**
- **Style transformation** is a pattern-learning task → benefits from fine-tuning
- **Job relevance** requires reasoning about requirements → better handled by a general-purpose LLM

---

## 🎨 Supported Styles

| Style | Description | Example Signal |
|-------|-------------|----------------|
| **Professional** | Polished, business-appropriate, measured confidence | "Spearheaded initiatives..." |
| **Academic** | Scholarly precision, methodological rigor | "Conducted systematic analysis..." |
| **Confident** | Bold assertions, outcome-first, strong ownership | "Delivered 40% improvement..." |
| **Concise** | Maximum impact, minimal words | "Led 8-person team. Cut costs 30%." |
| **Playful** | Warm, engaging, personality showing | "Built the thing that saved the day 🚀" |

---

## 🔧 Technical Details

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Base Model | LLaMA 3 8B (4-bit quantized) |
| Fine-tuning Method | LoRA (Low-Rank Adaptation) |
| LoRA Rank | 16 |
| LoRA Alpha | 32 |
| Target Modules | q_proj, k_proj, v_proj, o_proj, gate_proj, up_proj, down_proj |
| Trainable Parameters | 41.9M (0.92% of total) |
| Training Loss | 0.4053 |
| Training Time | 13.7 minutes |
| Hardware | NVIDIA A100-SXM4-40GB |

### Dataset

| Dimension | Count |
|-----------|-------|
| Total Examples | 1,050 |
| Training Set | 840 (80%) |
| Validation Set | 105 (10%) |
| Test Set | 105 (10%) |
| Styles | 5 |
| Section Types | 5 (Summary, Experience, Education, Skills, Projects) |
| Role Categories | 5 (Tech, Business, Creative, Healthcare, Academic) |
| Seniority Levels | 4 (Entry, Mid, Senior, Executive) |

All training data is **synthetically generated** to avoid privacy concerns with real CVs.

### Evaluation Methodology

- **LLM-as-Judge**: Claude API scores outputs on 3 dimensions (1-5 scale)
- **Metrics**: Style Fidelity, Factual Consistency, Quality
- **Comparison**: Fine-tuned LoRA vs Base Model (zero-shot)
- **Sample Size**: 25 examples (5 per style)

<details>
<summary>⚠️ Known Limitations</summary>

- LLM-as-judge may have self-preference bias
- Evaluation sample is relatively small (25 examples)
- Some style transformations are subtle when input is already well-written
- Model trained on English CVs only

</details>

---

## 📁 Project Structure

```
CameleonCV/
├── data/
│   ├── train.jsonl          # 840 training examples
│   ├── validation.jsonl     # 105 validation examples
│   └── test.jsonl           # 105 test examples
├── notebooks/
│   ├── training.ipynb       # LoRA fine-tuning notebook
│   └── evaluation.ipynb     # Model evaluation notebook
├── outputs/
│   ├── cameleon_lora_*/     # Saved LoRA adapter
│   ├── evaluation_report.md # Evaluation results
│   └── evaluation_chart.png # Results visualization
├── docs/
│   ├── style-definitions.md # Detailed style specifications
│   ├── dataset-schema.md    # Data format documentation
│   └── architecture.md      # System design details
└── cameleon-landing/        # React/Vite demo site
```

---

## 🚀 Quick Start

### Prerequisites
- Google Colab Pro (for A100 GPU access)
- ~2 hours for full training + evaluation

### Training

1. Upload training data to Google Drive:
```
My Drive/CameleonCV/data/
  ├── train.jsonl
  ├── validation.jsonl
  └── test.jsonl
```

2. Open `training.ipynb` in Google Colab

3. Select **A100 GPU** runtime

4. Run all cells (~15 min training)

### Inference

```python
from unsloth import FastLanguageModel

# Load fine-tuned model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="path/to/cameleon_lora_adapter",
    max_seq_length=2048,
    load_in_4bit=True,
)
FastLanguageModel.for_inference(model)

# Generate transformation
prompt = """### TASK
Rewrite the following CV section in confident style.

### ORIGINAL CV SECTION
Managed a team of 8 customer service representatives...

### REWRITTEN SECTION
"""

inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=256)
print(tokenizer.decode(outputs[0]))
```

---

## 📈 Roadmap

- [x] Dataset: 1,050 synthetic training examples
- [x] Training: LoRA fine-tuning on LLaMA 3 8B
- [x] Evaluation: LLM-as-judge comparison vs baseline
- [x] Landing page: Live at [cameleonai.eu](https://cameleonai.eu)
- [ ] Claude API integration for job relevance
- [ ] Interactive demo interface
- [ ] Hugging Face model release

---

## 🤔 Design Decisions

<details>
<summary><b>Why LoRA instead of full fine-tuning?</b></summary>

LoRA trains only 0.92% of parameters while achieving comparable results to full fine-tuning. This makes training feasible on consumer GPUs and keeps the adapter small (~160MB vs ~16GB for full model).

</details>

<details>
<summary><b>Why synthetic data?</b></summary>

Real CVs contain personal information. Synthetic data avoids privacy concerns while allowing precise control over style variations and balanced coverage across section types, industries, and seniority levels.

</details>

<details>
<summary><b>Why two-stage architecture?</b></summary>

Style transformation is a pattern-learning task that benefits from fine-tuning on examples. Job relevance requires reasoning about requirements and matching — something general-purpose LLMs already excel at. Separating these concerns allows independent iteration and optimal tool selection for each task.

</details>

<details>
<summary><b>Why LLM-as-judge for evaluation?</b></summary>

Style quality is subjective and hard to capture with traditional metrics like BLEU or ROUGE. LLM judges can assess nuanced qualities like "does this sound confident?" while providing interpretable scores. We acknowledge potential biases and report them as limitations.

</details>

---

## 📚 References

- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [Unsloth: Fast LLM Fine-tuning](https://github.com/unslothai/unsloth)
- [LLaMA 3 Technical Report](https://ai.meta.com/blog/meta-llama-3/)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Georgie** — [LinkedIn](https://linkedin.com/in/yourprofile) | [Portfolio](https://yourportfolio.com)

*Built as a portfolio project demonstrating ML engineering, prompt engineering, and product thinking.*