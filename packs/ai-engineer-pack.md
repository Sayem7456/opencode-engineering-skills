# AI Engineer Pack

## Who This Is For

Engineers building, evaluating, and deploying LLM-powered applications. Suitable for AI/ML engineers, prompt engineers, and teams building RAG pipelines or model-serving infrastructure.

## Included Skills

| Skill | Status | Purpose |
|-------|--------|---------|
| `python-quality` | Available | Production-quality Python, typing, error handling |
| `testing-and-debugging` | Available | Reproduction, root-cause analysis, regression tests |
| `llm-app-security` | Available | Review and harden LLM apps against prompt injection, data leakage, unsafe tool use and untrusted output |
| `prompt-injection-defense` | Available | Design, review and implement defenses against direct and indirect prompt injection |
| `rag-quality-review` | Available | Review and improve RAG systems for chunking, retrieval, grounding, citations, evaluation and safety |
| `ai-evaluation` | **Planned** | Systematic evaluation of LLM outputs, metrics, and benchmarks |
| `model-serving-production` | **Planned** | Deploying and operating LLM inference endpoints at scale |
| `token-saver` | Available | Efficient reading for large AI outputs and logs |
| `structured-output-reliability` | Available | JSON schemas, validation, retries, repair strategies, and downstream safety for LLM output |
| `context-engineering` | Available | Structured context for multi-step AI debugging |

> **Note:** Three skills are marked as **Planned**. They do not yet exist in this repository. The pack can be used with the available skills today. Planned skills will be added in future releases.

## Recommended Commands

- `/debug` — investigate LLM output quality or pipeline failures
- `/fix` — fix a confirmed defect in AI pipeline code
- `/plan` — plan AI feature implementation before editing
- `/context-audit` — audit context usage when working with large AI traces
- `/compress-context` — compress findings from long AI debugging sessions

## Best Use Cases

- Building a RAG pipeline with retrieval and generation
- Debugging poor LLM response quality or hallucination
- Implementing guardrails against prompt injection
- Evaluating model output quality with structured metrics
- Deploying an LLM inference endpoint to production

## Example Prompts

```
Use ai-engineer-pack to build a RAG pipeline that retrieves relevant documentation and generates answers with citations.
```

```
Use ai-engineer-pack to debug why the LLM sometimes ignores system instructions and reveals internal prompts.
```

```
Use ai-engineer-pack to evaluate the quality of the generated summaries against a labeled test set.
```

## Installation

```bash
npx skills add Sayem7456/opencode-engineering-skills \
  --skill python-quality \
  --skill testing-and-debugging \
  --skill token-saver \
  --skill context-engineering \
  --skill structured-output-reliability \
  --skill llm-app-security \
  --skill prompt-injection-defense \
  --skill rag-quality-review \
  --agent opencode \
  --global
```

To also install the slash commands:

```bash
git clone https://github.com/Sayem7456/opencode-engineering-skills.git
cd opencode-engineering-skills
chmod +x scripts/install-opencode.sh
./scripts/install-opencode.sh
```

## When Not to Use

- Traditional CRUD backend work without AI components (use backend-pack)
- Frontend-only UI work (use frontend-pack)
- Production deployment review without AI-specific concerns (use production-pack)
