---
name: fine-tuning
description: Fine-tune LLMs using Axolotl, Unsloth, TRL or LLaMA-Factory, covering data preparation, training configuration, LoRA/QLoRA, evaluation, deployment and safety.
license: MIT
compatibility: opencode
metadata:
  category: ai-engineering
  stack: fine-tuning
  version: "1.0.0"
---

# Fine-Tuning

Use this skill when fine-tuning a large language model for a specific task or domain — including data preparation, training configuration, evaluation, and deployment of the fine-tuned model.

The objective is to produce a fine-tuned model that improves task performance without regressing on general capabilities, introducing safety vulnerabilities, or wasting compute.

## When to Use This Skill

Load this skill when the task involves any of the following:

- deciding whether to fine-tune, prompt-engineer, or use RAG for a task
- preparing a training dataset for fine-tuning
- configuring a training run with Axolotl, Unsloth, TRL, or LLaMA-Factory
- applying parameter-efficient methods (LoRA, QLoRA, DoRA)
- evaluating a fine-tuned model against the base model
- deploying a fine-tuned model to production
- auditing a fine-tuning pipeline for data quality, leakage, or safety

Do not load this skill for:

- general prompt engineering (use prompt-injection-defense skill)
- RAG pipeline design (use rag-quality-review skill)
- model evaluation methodology (use ai-evaluation skill)
- model-serving infrastructure (use model-serving-production skill)

## Decision: Fine-Tune vs. Alternatives

Before fine-tuning, evaluate whether the goal can be achieved with cheaper or lower-risk alternatives.

| Approach | Cost | Risk | Best For |
|----------|------|------|----------|
| Prompt engineering | Low | Low | Simple formatting or style changes |
| Few-shot prompting | Low | Low | Tasks with clear examples |
| RAG | Medium | Low | Knowledge-grounded tasks |
| Fine-tuning (LoRA) | Medium | Medium | Task-specific behavior, consistent output format |
| Fine-tuning (full) | High | High | Domain adaptation, new capabilities |

### When Fine-Tuning Is Appropriate

- the task requires consistent output structure that prompting cannot enforce
- the model must learn domain-specific terminology or style
- the task has a clear input-output mapping with hundreds to thousands of examples
- latency or cost constraints make prompt-based approaches infeasible

### When Fine-Tuning Is Not Appropriate

- the task can be solved with a well-written prompt and a few examples
- the knowledge required changes frequently (prefer RAG)
- the training data contains factual information the base model already knows
- the dataset is smaller than ~100 high-quality examples
- the fine-tuning objective is to add new factual knowledge (models memorize poorly)

## Data Preparation

### Dataset Requirements

Every fine-tuning dataset must have:

- **Clear task definition** — what input maps to what output
- **Consistent formatting** — all examples follow the same template
- **Label quality** — every example verified by a human or high-precision automated process
- **Stratified split** — train/validation/test splits that reflect real-world distribution
- **No leakage** — no overlap between train and test examples, and no base-model memorization targets

### Format by Framework

**Chat format (TRL, Axolotl, LLaMA-Factory):**

```json
[
  {
    "conversations": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "What is the capital of France?"},
      {"role": "assistant", "content": "The capital of France is Paris."}
    ]
  }
]
```

**Completion format (Unsloth, Axolotl):**

```json
[
  {
    "instruction": "What is the capital of France?",
    "output": "The capital of France is Paris."
  }
]
```

### Data Quality Checks

Before training, validate the dataset:

- [ ] No duplicate examples across train and test splits
- [ ] No empty or null inputs or outputs
- [ ] Consistent vocabulary, formatting, and punctuation across examples
- [ ] Label distribution matches the real-world use case
- [ ] No PII, secrets, or credentials in the training data
- [ ] No toxic, biased, or harmful content (unless the task requires it and safeguards exist)
- [ ] Input length does not exceed the model's context window
- [ ] Output length is appropriate for the task (not truncated by max_length)

### Detecting Data Leakage

Test for overlap between your dataset and the base model's training data:

```python
def check_leakage(dataset: list[dict], model: str, sample_ratio: float = 0.1) -> dict:
    """Sample examples and prompt the base model to detect memorized content."""
    import random
    sample = random.sample(dataset, int(len(dataset) * sample_ratio))
    results = {"exact_match": 0, "partial_match": 0, "no_match": 0}
    for example in sample:
        prompt = example.get("instruction", example.get("user", ""))
        expected = example.get("output", example.get("assistant", ""))
        # Skip examples where the base model already produces the target output
        # These examples add no training signal
    return results
```

## Framework Comparison

| Framework | Strengths | Best For |
|-----------|-----------|----------|
| **Axolotl** | Full training control, multi-GPU, extensive model support | Production fine-tuning, large-scale training |
| **Unsloth** | 2x faster LoRA/QLoRA, reduced memory, FP4 support | Rapid iteration, single-GPU, limited budget |
| **TRL** | HuggingFace ecosystem, PPO/DPO/GRPO support, best docs | Reinforcement learning, preference tuning |
| **LLaMA-Factory** | Web UI, broad model support, easy setup | Quick experiments, non-engineers, small teams |

### Installation

```bash
# Axolotl
pip install axolotl

# Unsloth
pip install unsloth

# TRL
pip install trl

# LLaMA-Factory
pip install llama-factory
```

## Training Configuration

### Choosing a Method

| Method | Memory | Speed | Quality | When to Use |
|--------|--------|-------|---------|-------------|
| Full fine-tune | Very high | Slow | Best | Large compute budget, domain adaptation |
| LoRA (r=16-64) | Low | Fast | Good | Most tasks, limited GPU memory |
| QLoRA (4-bit) | Very low | Fast | Adequate | Single GPU, limited budget, rapid iteration |
| DoRA | Low | Fast | Better than LoRA | Tasks needing closer-to-full quality |

### LoRA Configuration

```yaml
# LoRA hyperparameters (YAML config for Axolotl / LLaMA-Factory)
lora_r: 16
lora_alpha: 32
lora_dropout: 0.05
lora_target_modules:
  - q_proj
  - k_proj
  - v_proj
  - o_proj
  - gate_proj
  - up_proj
  - down_proj
```

Rule of thumb: `alpha = 2 * r`. Start with `r=16` and increase if underfitting, decrease if overfitting.

### Training Hyperparameters

```yaml
# Common starting point for 7B-8B parameter models
per_device_train_batch_size: 4
per_device_eval_batch_size: 4
gradient_accumulation_steps: 4
learning_rate: 2e-4
num_train_epochs: 3
warmup_ratio: 0.03
lr_scheduler_type: cosine
optim: adamw_8bit
bf16: true
tf32: true
max_grad_norm: 1.0
save_strategy: steps
save_steps: 100
eval_strategy: steps
eval_steps: 100
logging_steps: 10
```

### Learning Rate Guidelines

| Method | Learning Rate |
|--------|--------------|
| Full fine-tune | 1e-5 to 5e-5 |
| LoRA | 1e-4 to 5e-4 |
| QLoRA | 1e-4 to 3e-4 |
| DoRA | 1e-4 to 3e-4 |

## Evaluation

### Pre-Training Baseline

Before fine-tuning, evaluate the base model on your task's metrics:

```python
def evaluate_model(model, dataset: list[dict]) -> dict:
    """Evaluate a model on a held-out test set."""
    results = {"accuracy": 0.0, "f1": 0.0, "latency_ms": 0.0}
    correct = 0
    for example in dataset:
        prediction = model.generate(example["input"])
        if prediction.strip() == example["expected"].strip():
            correct += 1
    results["accuracy"] = correct / len(dataset)
    return results
```

Compare the fine-tuned model against the base model using the same metrics. A fine-tuning run is successful only if the fine-tuned model outperforms the base on the target task without regressing on general benchmarks.

### Evaluation Checklist

- [ ] Same test set used for base model and fine-tuned model
- [ ] Metrics include task-specific scores AND general capability retention
- [ ] Statistical significance test applied (paired bootstrap or McNemar's)
- [ ] Human evaluation for subjective quality (if applicable)
- [ ] Safety evaluation: red-teaming the fine-tuned model

### Retention Benchmarks

Test the fine-tuned model on standard benchmarks to detect capability regression:

- MMLU (knowledge and reasoning)
- HellaSwag (commonsense inference)
- GSM8K (math)
- HumanEval or MBPP (code)
- TruthfulQA (honesty)

A fine-tuned model should not drop more than 2-3% on any benchmark unless the drop is understood and acceptable for the use case.

## Safety and Security

### Data Safety

- **Scan for PII** before training. Remove or redact personal information.
- **Scan for toxic content.** Fine-tuning on biased or toxic data amplifies those behaviors.
- **Scan for secrets.** API keys, passwords, and internal URLs in training data will be memorized.
- **Retain data provenance.** Know the source of every training example for audit trails.

### Model Safety

- **Red-team the fine-tuned model.** Prompt injection, jailbreak attempts, and role-play attacks may succeed more easily after fine-tuning.
- **Test refusal behavior.** Fine-tuning can accidentally unlearn safety guardrails. Verify the model still refuses harmful requests.
- **Evaluate honesty.** Fine-tuning on factual data can reduce hallucination, but fine-tuning on synthetic or unverified data increases it.

```python
def safety_evaluation(model, test_cases: list[dict]) -> dict:
    """Test refusal rates for harmful and benign prompts."""
    results = {"harmful_refusal_rate": 0.0, "benign_refusal_rate": 0.0}
    harmful_refused = 0
    for case in test_cases:
        response = model.generate(case["prompt"])
        if case["is_harmful"] and "cannot" in response.lower():
            harmful_refused += 1
    results["harmful_refusal_rate"] = harmful_refused / sum(1 for c in test_cases if c["is_harmful"])
    return results
```

### Deployment Safety

- Use a content safety classifier as a guardrail on model output
- Implement rate limiting per user or tenant
- Log all inputs and outputs for audit (without PII)
- Have a manual override or fallback to the base model if quality degrades

## Production Deployment

### Exporting the Model

```python
# Save adapter weights (LoRA)
model.save_pretrained("./my-fine-tune-lora")

# Merge and save full weights
from unsloth import FastLanguageModel
model = FastLanguageModel.get_peft_model(model, ...)
model.save_pretrained_merged("./my-fine-tune-merged", tokenizer, save_method="merged_16bit")
```

### Serving the Fine-Tuned Model

For LoRA adapters, use a serving framework that supports dynamic adapter loading:

```bash
# vLLM with LoRA
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-3.1-8B \
    --enable-lora \
    --lora-modules my-task=./my-fine-tune-lora
```

For merged models, serve as a standard model:

```bash
# TGI
text-generation-launcher --model-id ./my-fine-tune-merged

# vLLM
python -m vllm.entrypoints.openai.api_server \
    --model ./my-fine-tune-merged
```

### Monitoring

- Track generation quality metrics (accuracy, faithfulness, refusal rate)
- Monitor latency (p50/p95/p99) and throughput
- Detect drift: periodically evaluate the deployed model against the held-out test set
- Set up an automated re-evaluation trigger when quality metrics drop below a threshold

## Testing a Fine-Tuning Pipeline

### Unit Tests

```python
def test_dataset_format():
    examples = load_dataset("my-task")
    for ex in examples:
        assert "instruction" in ex and "output" in ex
        assert len(ex["instruction"]) > 0

def test_no_train_test_leakage():
    train, test = load_splits()
    train_inputs = {ex["instruction"] for ex in train}
    test_inputs = {ex["instruction"] for ex in test}
    assert len(train_inputs & test_inputs) == 0
```

### Integration Tests

```python
@pytest.mark.slow
def test_training_loop():
    """Train on a tiny dataset to verify the pipeline runs end to end."""
    config = load_training_config()
    config.num_train_epochs = 1
    config.max_steps = 10
    model = train(config)
    assert model is not None
    assert model.config.adapter_config is not None  # LoRA was applied
```

### Regression Tests

- [ ] Training is reproducible with a fixed seed
- [ ] Training can resume from a checkpoint
- [ ] Evaluation metrics are computed correctly
- [ ] Model export produces a loadable artifact
- [ ] The fine-tuned model refuses harmful requests at the same rate as the base model

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Fine-tuning on noisy data | Model learns errors instead of patterns | Clean and validate every example |
| Overly large learning rate | Training diverges or loss spikes | Start with recommended LR for the method |
| Training too few steps | Model underfits | Monitor eval loss; train until it plateaus |
| Training too many steps | Model overfits or catastrophic forgetting | Use early stopping; evaluate periodically |
| Ignoring base model evaluation | Cannot measure improvement | Always evaluate the base model first |
| Fine-tuning on memorized data | No training signal; wasted compute | Run leakage detection before training |
| No safety evaluation | Fine-tuning may remove safety guardrails | Red-team the fine-tuned model before deployment |
| Training on synthetic data only | Model amplifies synthetic errors | Use human-verified data for the test set |

## Completion Criteria

A fine-tuning pipeline is complete only when:

- [ ] the decision to fine-tune (vs. prompt engineering or RAG) is documented and justified
- [ ] the dataset passes all quality checks (no duplicates, no leakage, no PII)
- [ ] the base model is evaluated on the target task before training
- [ ] training hyperparameters are chosen based on the method (full, LoRA, QLoRA, DoRA)
- [ ] eval loss is monitored and training is stopped before overfitting
- [ ] the fine-tuned model outperforms the base model on the target task
- [ ] general capability regression is measured and acceptable
- [ ] safety evaluation (refusal rate, toxic output, jailbreak resistance) passes
- [ ] the model artifact can be exported, loaded, and served
- [ ] a monitoring plan exists for production deployment

## Related Skills

- `ai-evaluation` — for rigorous evaluation methodology and metric selection
- `rag-quality-review` — for comparing fine-tuning vs. RAG as an alternative
- `model-serving-production` — for deploying the fine-tuned model
- `prompt-injection-defense` — for red-teaming and safety evaluation of the fine-tuned model
- `python-quality` — for production-quality training script implementation
