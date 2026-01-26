# Dataset Schema

This document defines the data format, validation rules, and quality standards for CameleonCV training data.

---

## Overview

| Property | Value |
|----------|-------|
| Format | JSONL (JSON Lines) |
| Encoding | UTF-8 |
| One example per line | Yes |
| Target size | ~1,050 examples |
| Split ratio | 80% train / 10% validation / 10% test |

---

## Schema Definition

### Full Example

```json
{
  "example_id": "seed_001_confident",
  "metadata": {
    "seed_id": "seed_001",
    "section_type": "summary",
    "target_style": "confident",
    "role_category": "technical",
    "seniority": "entry-level",
    "source_type": "synthetic",
    "transformation_intensity": "high",
    "created_at": "2025-01-20T14:30:00Z",
    "validated_at": "2025-01-21T09:15:00Z",
    "notes": ""
  },
  "input": {
    "original_section": "Recent computer science graduate with hands-on experience...",
    "job_posting_excerpt": "**Junior Full-Stack Developer**\n\nWe're seeking...",
    "instructions": "Rewrite this CV summary in a confident style. Preserve all facts exactly. Use strong action verbs and direct assertions."
  },
  "target_output": "Delivered measurable impact as a full-stack developer...",
  "validation": {
    "factual_score": 5,
    "style_score": 4,
    "quality_score": 5,
    "status": "approved",
    "issues": []
  }
}
```

---

## Field Specifications

### Root Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `example_id` | string | Yes | Unique identifier: `{seed_id}_{style}` |
| `metadata` | object | Yes | Categorization and provenance |
| `input` | object | Yes | Model input components |
| `target_output` | string | Yes | Expected model output |
| `validation` | object | No | Quality scores (added post-validation) |

### Metadata Object

| Field | Type | Required | Allowed Values |
|-------|------|----------|----------------|
| `seed_id` | string | Yes | `seed_001` through `seed_210` |
| `section_type` | enum | Yes | `summary`, `experience`, `education`, `skills`, `projects` |
| `target_style` | enum | Yes | `professional`, `academic`, `confident`, `concise`, `playful` |
| `role_category` | enum | Yes | `technical`, `business`, `creative`, `academic`, `operations` |
| `seniority` | enum | Yes | `entry-level`, `mid-level`, `senior`, `executive` |
| `source_type` | enum | Yes | `synthetic`, `curated`, `augmented` |
| `transformation_intensity` | enum | No | `high`, `medium`, `low`, `none` |
| `created_at` | ISO 8601 | No | Timestamp of creation |
| `validated_at` | ISO 8601 | No | Timestamp of validation |
| `notes` | string | No | Free-form notes |

### Input Object

| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| `original_section` | string | Yes | 50-500 words typical |
| `job_posting_excerpt` | string | Yes | 75-150 words typical |
| `instructions` | string | Yes | Style-specific rewrite instructions |

### Validation Object

| Field | Type | Required | Allowed Values |
|-------|------|----------|----------------|
| `factual_score` | integer | No | 1-5 |
| `style_score` | integer | No | 1-5 |
| `quality_score` | integer | No | 1-5 |
| `status` | enum | No | `pending`, `approved`, `rejected` |
| `issues` | array | No | List of identified problems |

---

## Enum Definitions

### section_type

| Value | Description |
|-------|-------------|
| `summary` | Professional summary / objective statement |
| `experience` | Work experience entries |
| `education` | Educational background |
| `skills` | Technical and soft skills |
| `projects` | Personal, academic, or professional projects |

### target_style

| Value | Description |
|-------|-------------|
| `professional` | Polished, business-appropriate |
| `academic` | Scholarly, methodological |
| `confident` | Bold, assertive |
| `concise` | Maximum density, minimal words |
| `playful` | Personality-forward with icons |

### role_category

| Value | Example Roles |
|-------|---------------|
| `technical` | Software engineer, data scientist, DevOps |
| `business` | Product manager, analyst, consultant |
| `creative` | Designer, writer, marketing |
| `academic` | Researcher, professor, scientist |
| `operations` | Operations manager, supply chain, HR |

### seniority

| Value | Years Experience (Typical) |
|-------|---------------------------|
| `entry-level` | 0-2 years |
| `mid-level` | 3-7 years |
| `senior` | 8-15 years |
| `executive` | 15+ years |

### source_type

| Value | Description |
|-------|-------------|
| `synthetic` | Generated via LLM for this project |
| `curated` | Adapted from public templates |
| `augmented` | Modified version of existing example |

### transformation_intensity

| Value | Description |
|-------|-------------|
| `high` | Significant style shift from original |
| `medium` | Moderate changes |
| `low` | Minor refinements |
| `none` | Original already matched target style |

---

## Prompt Template

Training examples are assembled into this format:

```
### TASK
Rewrite the following CV section according to the specified style and constraints.

### ORIGINAL CV SECTION
{original_section}

### TARGET JOB CONTEXT
{job_posting_excerpt}

### INSTRUCTIONS
{instructions}

### REWRITTEN SECTION
{target_output}
```

The model learns to generate everything after `### REWRITTEN SECTION` given the preceding context.

---

## Dataset Distribution

### Target Counts

| Dimension | Categories | Examples Each | Total |
|-----------|------------|---------------|-------|
| Styles | 5 | 210 | 1,050 |
| Section types | 5 | 210 | 1,050 |
| Role categories | 5 | ~210 | 1,050 |
| Seniority levels | 4 | ~262 | 1,050 |

### Cross-Distribution Goals

Every combination should have representation:
- Each (style × section_type) pair: ≥40 examples
- Each (style × role_category) pair: ≥40 examples
- Each (section_type × role_category) pair: ≥8 examples

---

## Validation Rules

### Structural Validation

```python
def validate_structure(example):
    required_fields = ['example_id', 'metadata', 'input', 'target_output']
    required_metadata = ['seed_id', 'section_type', 'target_style', 'role_category', 'seniority', 'source_type']
    required_input = ['original_section', 'job_posting_excerpt', 'instructions']
    
    # Check all required fields exist
    # Check enum values are valid
    # Check string lengths are reasonable
    # Check example_id matches pattern: seed_XXX_style
```

### Semantic Validation

| Check | Method | Threshold |
|-------|--------|-----------|
| Factual preservation | Entity extraction comparison | 100% entities preserved |
| No hallucination | New entities in output | 0 new entities |
| Style adherence | LLM scoring against rubric | Score ≥ 4/5 |
| Quality | Grammar + professional suitability | Score ≥ 4/5 |

### Approval Criteria

An example is `approved` if:
- `factual_score` ≥ 4
- `style_score` ≥ 4
- `quality_score` ≥ 4
- No critical issues in `issues` array

---

## Scoring Rubrics

### Factual Score (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Perfect — every fact preserved exactly |
| 4 | Minor rewording but all facts accurate |
| 3 | Small omission OR slight embellishment |
| 2 | Noticeable fact changes or additions |
| 1 | Significant hallucination or invented information |

### Style Score (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Exemplary — clearly demonstrates target style |
| 4 | Good adherence with minor inconsistencies |
| 3 | Partial style application — mixed signals |
| 2 | Weak style presence — mostly neutral |
| 1 | Wrong style or no transformation |

### Quality Score (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Ready to submit — professional and polished |
| 4 | Good quality with minor improvements possible |
| 3 | Acceptable but noticeable issues |
| 2 | Needs revision — awkward or unclear |
| 1 | Unprofessional — would not use |

---

## File Organization

```
data/
├── raw/
│   ├── seeds.csv                    # 210 seed examples
│   └── transformations.csv          # 1,050 transformations (working file)
├── processed/
│   ├── approved.jsonl               # Validated examples
│   └── rejected.jsonl               # Failed validation
├── final/
│   ├── train.jsonl                  # 80% (~840 examples)
│   ├── validation.jsonl             # 10% (~105 examples)
│   └── test.jsonl                   # 10% (~105 examples)
└── schema/
    └── example.schema.json          # JSON Schema for validation
```

---

## JSON Schema (for automated validation)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["example_id", "metadata", "input", "target_output"],
  "properties": {
    "example_id": {
      "type": "string",
      "pattern": "^seed_\\d{3}_(professional|academic|confident|concise|playful)$"
    },
    "metadata": {
      "type": "object",
      "required": ["seed_id", "section_type", "target_style", "role_category", "seniority", "source_type"],
      "properties": {
        "seed_id": {
          "type": "string",
          "pattern": "^seed_\\d{3}$"
        },
        "section_type": {
          "type": "string",
          "enum": ["summary", "experience", "education", "skills", "projects"]
        },
        "target_style": {
          "type": "string",
          "enum": ["professional", "academic", "confident", "concise", "playful"]
        },
        "role_category": {
          "type": "string",
          "enum": ["technical", "business", "creative", "academic", "operations"]
        },
        "seniority": {
          "type": "string",
          "enum": ["entry-level", "mid-level", "senior", "executive"]
        },
        "source_type": {
          "type": "string",
          "enum": ["synthetic", "curated", "augmented"]
        }
      }
    },
    "input": {
      "type": "object",
      "required": ["original_section", "job_posting_excerpt", "instructions"],
      "properties": {
        "original_section": {
          "type": "string",
          "minLength": 50,
          "maxLength": 5000
        },
        "job_posting_excerpt": {
          "type": "string",
          "minLength": 50,
          "maxLength": 2000
        },
        "instructions": {
          "type": "string",
          "minLength": 10,
          "maxLength": 1000
        }
      }
    },
    "target_output": {
      "type": "string",
      "minLength": 20,
      "maxLength": 5000
    }
  }
}
```

---

## Versioning

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-20 | Initial schema |
| 1.1 | 2025-01-21 | Added transformation_intensity field |
| 1.2 | TBD | Post-training refinements |

---

## Notes for Training

### Tokenization Considerations

- Average example length: ~500-800 tokens
- Maximum sequence length: 2048 tokens (fits all examples)
- Special tokens: None required beyond model defaults

### Data Loading

```python
from datasets import load_dataset

dataset = load_dataset('json', data_files={
    'train': 'data/final/train.jsonl',
    'validation': 'data/final/validation.jsonl',
    'test': 'data/final/test.jsonl'
})
```

### Formatting Function

```python
def format_example(example):
    """Convert dataset example to training text."""
    return f"""### TASK
Rewrite the following CV section according to the specified style and constraints.

### ORIGINAL CV SECTION
{example['input']['original_section']}

### TARGET JOB CONTEXT
{example['input']['job_posting_excerpt']}

### INSTRUCTIONS
{example['input']['instructions']}

### REWRITTEN SECTION
{example['target_output']}"""
```
