# 🦎 CameleonCV

**AI-powered CV transformation that adapts writing style and job relevance.**

Transform any CV section into 5 distinct writing styles while preserving factual accuracy. Two-stage pipeline: LoRA fine-tuning for style, Claude API for job relevance.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://cameleonai.eu)
[![Model](https://img.shields.io/badge/🤗%20Model-HuggingFace-yellow)](https://huggingface.co/georgieslab/cameleon-cv-lora)
[![API](https://img.shields.io/badge/API-Modal-purple)](https://modal.com)
[![Training](https://img.shields.io/badge/training-LoRA-orange)](https://arxiv.org/abs/2106.09685)

---

## 🎬 Live Demo

**Try it now:** [cameleonai.eu](https://cameleonai.eu)

### Example Output (Professional + Job-Tailored)

**Input:**
> Developed and maintained RESTful APIs serving 50,000+ daily active users. Reduced page load times by 40% through code optimization and caching strategies. Collaborated with the QA team to improve test coverage from 65% to 90%.

**Job Posting:** Senior Backend Engineer at FinTech startup seeking scalable systems, high-traffic APIs, performance optimization...

**Output:**
> Developed, deployed, and maintained scalable RESTful API architectures serving 50,000+ daily active users in high-performance environments. Engineered performance-critical optimizations reducing page load times by 40% through advanced caching and code efficiency strategies. Collaborated closely with QA team to drive comprehensive testing protocols, systematically increasing test coverage from 65% to 90%, ensuring system reliability and robust technical quality.

✅ All facts preserved · ✅ Job keywords added · ✅ Professional tone applied

---

## 📊 Evaluation Results

Fine-tuned model vs zero-shot baseline using LLM-as-judge methodology:

| Metric | Base Model | Fine-tuned | Improvement |
|--------|-----------|------------|-------------|
| Style Fidelity | 2.48 | 3.64 | **+47%** |
| Factual Consistency | 4.28 | 4.60 | +7% |
| Quality | 3.24 | 3.92 | +21% |
| **Overall** | 3.33 | **4.05** | **+22%** |

**Win Rate:** Fine-tuned model outperforms base model in **76%** of head-to-head comparisons.

<details>
<summary>📈 Results by Style</summary>

| Style | Base Avg | Fine-tuned Avg | Δ | Production Quality |
|-------|----------|----------------|---|-------------------|
| Professional | 3.2 | 4.1 | +0.9 | ⭐ Best |
| Confident | 3.4 | 4.2 | +0.8 | ✅ Good |
| Academic | 3.1 | 3.9 | +0.8 | ✅ Good |
| Playful | 3.4 | 4.0 | +0.6 | ⚠️ Variable |
| Concise | 3.5 | 4.3 | +0.8 | ⚠️ Variable |

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
│              Stage 1: Style Transformation ✅                │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │           LoRA-adapted LLaMA 3.1 (8B)               │   │
│   │                                                     │   │
│   │   • Pattern learning task (fine-tuned)              │   │
│   │   • 5 distinct style transformations                │   │
│   │   • Trained on 1,050 synthetic examples             │   │
│   │   • 4-bit quantization for efficient inference      │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Stage 2: Job Relevance ✅                       │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                Claude 3.5 Haiku API                 │   │
│   │                                                     │   │
│   │   • Reasoning task (no training needed)             │   │
│   │   • Matches skills to job requirements              │   │
│   │   • Adds relevant keywords naturally                │   │
│   │   • Fact verification prevents hallucination        │   │
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
- **Job relevance** requires reasoning about requirements → better handled by general-purpose LLM
- **Separation of concerns** → can iterate on each independently

---

## 🎨 Supported Styles

| Style | Description | Best For | Quality |
|-------|-------------|----------|---------|
| **Professional** | Polished, business-appropriate, measured confidence | Corporate roles, consulting | ⭐ Best |
| **Confident** | Bold assertions, outcome-first, strong ownership | Leadership, sales, startups | ✅ Good |
| **Academic** | Scholarly precision, methodological rigor | Research, education, grants | ✅ Good |
| **Playful** | Warm, engaging, personality showing | Creative roles, startups | ⚠️ Variable |
| **Concise** | Maximum impact, minimal words | Executive summaries | ⚠️ Variable |

**Recommendation:** Use Professional or Confident with a job posting for best results.

---

## 🔧 Technical Stack

### Deployment

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Model Hosting** | Modal.com (A10G GPU) | LoRA inference with 4-bit quantization |
| **Job Relevance** | Claude 3.5 Haiku API | Reasoning + fact verification |
| **Frontend** | React + Vite | Interactive demo |
| **Hosting** | Vercel | Landing page at cameleonai.eu |
| **Model Registry** | HuggingFace Hub | LoRA adapter storage |

### Training Configuration

| Parameter | Value |
|-----------|-------|
| Base Model | LLaMA 3.1 8B Instruct (4-bit quantized) |
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

---

## ⚠️ Known Limitations

### Model Behavior
- **Concise style** sometimes produces garbled output with broken formatting
- **Playful style** can be inconsistent with emoji placement
- **Short inputs** (<15 words) may cause hallucination — model trained on full CV sections
- **Number drift** occasionally occurs (e.g., 40% → 45%) — mitigated by fact verification

### Technical Constraints
- **Cold start**: First request takes ~60s (model loading)
- **Quantization**: 4-bit reduces precision slightly vs full precision
- **Context window**: Best with 2-4 sentence inputs
- **English only**: Model trained exclusively on English CVs

### Evaluation Caveats
- LLM-as-judge may have self-preference bias
- Evaluation sample is relatively small (25 examples)
- Style quality is inherently subjective

---

## 📁 Project Structure

```
CameleonCV/
├── data/
│   ├── train.jsonl              # 840 training examples
│   ├── validation.jsonl         # 105 validation examples
│   └── test.jsonl               # 105 test examples
├── notebooks/
│   ├── training.ipynb           # LoRA fine-tuning notebook
│   └── evaluation.ipynb         # Model evaluation notebook
├── outputs/
│   ├── cameleon_lora_*/         # Saved LoRA adapter
│   ├── evaluation_report.md     # Evaluation results
│   └── evaluation_chart.png     # Results visualization
├── docs/
│   ├── style-definitions.md     # Detailed style specifications
│   ├── dataset-schema.md        # Data format documentation
│   └── architecture.md          # System design details
├── cameleon-landing/            # React/Vite demo site (Vercel)
└── cameleon-modal/              # Modal API deployment
    └── cameleon_api.py          # Two-stage pipeline
```

---

## 🚀 Quick Start

### Try the Demo
Visit [cameleonai.eu](https://cameleonai.eu) and paste a CV section.

### Run Locally

**Prerequisites:**
- Modal account ([modal.com](https://modal.com))
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Python 3.11+

**Setup:**
```bash
# Clone repository
git clone https://github.com/georgieslab/CameleonCV.git
cd CameleonCV/cameleon-modal

# Install Modal CLI
pip install modal

# Add Anthropic API key as Modal secret
modal secret create anthropic-api-key ANTHROPIC_API_KEY=sk-ant-xxxxx

# Deploy
modal deploy cameleon_api.py
```

### Training (Colab)

1. Upload training data to Google Drive
2. Open `notebooks/training.ipynb` in Google Colab
3. Select **A100 GPU** runtime
4. Run all cells (~15 min)

---

## 📈 Roadmap

- [x] Dataset: 1,050 synthetic training examples
- [x] Training: LoRA fine-tuning on LLaMA 3.1 8B
- [x] Evaluation: LLM-as-judge comparison vs baseline
- [x] Landing page: Live at [cameleonai.eu](https://cameleonai.eu)
- [x] Model hosting: HuggingFace Hub + Modal deployment
- [x] Claude API integration for job relevance
- [x] Interactive demo with live API
- [x] Fact verification layer
- [ ] Improve Concise/Playful style quality (requires retraining)
- [ ] Add more section type support
- [ ] Multi-language support

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

<details>
<summary><b>Why fact verification?</b></summary>

LLMs can "drift" numbers during rewriting (e.g., 40% → 45%). The fact verification layer extracts all numbers from the original input and checks they appear exactly in the output. If verification fails, we fall back to the styled-only version.

</details>

<details>
<summary><b>Why prompt format matters?</b></summary>

LoRA adapters are pattern-sensitive. The production prompt must match the training format exactly (`### Instruction / ### Input / ### Response`) or the adapter won't activate properly, causing the base model's verbose behavior to dominate.

</details>

---

## 🎓 Interview Talking Points

This project demonstrates:

1. **ML Engineering**: LoRA fine-tuning, 4-bit quantization, prompt format alignment
2. **System Design**: Two-stage pipeline separating learned behavior from reasoning
3. **Evaluation Methodology**: LLM-as-judge with explicit limitations
4. **Production Deployment**: Modal GPU hosting, Vercel frontend, HuggingFace model registry
5. **Honest Engineering**: Documented limitations, fact verification fallbacks, realistic demo

**Key insight:** The prompt format mismatch between training and inference was the hardest bug to diagnose — LoRA adapters are pattern detectors that fail silently when patterns don't match.

---

## 📚 References

- [LoRA: Low-Rank Adaptation of Large Language Models](https://arxiv.org/abs/2106.09685)
- [Unsloth: Fast LLM Fine-tuning](https://github.com/unslothai/unsloth)
- [LLaMA 3 Technical Report](https://ai.meta.com/blog/meta-llama-3/)
- [Claude API Documentation](https://docs.anthropic.com)

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👤 Author

**Georgie** — [LinkedIn](https://linkedin.com/in/georgieslab) | [Email](mailto:georgslab@icloud.com)

*Built as a portfolio project demonstrating ML engineering, prompt engineering, and product thinking.*

---

<p align="center">
  <a href="https://cameleonai.eu">🦎 Try the Live Demo</a>
</p>