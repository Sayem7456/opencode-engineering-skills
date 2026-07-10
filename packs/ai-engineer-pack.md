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
| `ai-evaluation` | Available | Design and review evaluation workflows for LLM, RAG and AI systems |
| `ai-cost-optimization` | Available | Optimize LLM and AI application cost through caching, routing, batching and budgets |
| `model-serving-production` | Available | Design, review and harden production AI model-serving systems |
| `token-saver` | Available | Efficient reading for large AI outputs and logs |
| `structured-output-reliability` | Available | JSON schemas, validation, retries, repair strategies, and downstream safety for LLM output |
| `context-engineering` | Available | Structured context for multi-step AI debugging |
| `mcp-development` | New | Build, test, debug and deploy MCP servers for tools, resources and prompts |
| `multi-agent-orchestration` | New | Design multi-agent workflows with subagent decomposition, parallel execution and error recovery |
| `fine-tuning` | New | Fine-tune LLMs with Axolotl, Unsloth, TRL or LLaMA-Factory, covering data prep, training config, evaluation and deployment |
| `llm-observability` | New | Design and implement observability for LLM applications, including tracing, metrics, cost tracking, online evaluation, alerting and dashboards |
| `prompt-engineering` | New | Design, test, and optimize prompts for LLMs, including system prompts, few-shot, chain-of-thought, template management, technique selection and versioning |
| `ai-system-architecture` | New | Design, review and document AI system architecture, covering problem framing, model vs. rule decisions, LLM/RAG/ML pipelines, ingestion, retrieval, orchestration, evaluation, serving, safety, privacy, lifecycle and failure modes |

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
- Building MCP servers to expose tools and resources to AI agents
- Orchestrating multi-agent pipelines for complex engineering tasks
- Fine-tuning a language model for domain-specific tasks
- Observing LLM behavior in production with tracing, cost tracking, and quality monitoring
- Designing and testing prompts systematically for consistent LLM output

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

```
Use ai-engineer-pack to build an MCP server that exposes internal APIs as agent-callable tools with authentication and rate limiting.
```

```
Use ai-engineer-pack to orchestrate a multi-agent pipeline where a researcher agent finds relevant docs, a planner agent designs the implementation, and a builder agent writes the code.
```

```
Use ai-engineer-pack to fine-tune a Llama model on customer support conversations using LoRA, evaluate the result, and deploy the adapter to production.
```

```
Use ai-engineer-pack to add observability to a production LLM chat service, tracing each request from prompt to response with cost attribution, latency tracking, and quality scoring.
```

```
Use ai-engineer-pack to design and test a system prompt for a code review assistant, selecting the right technique, writing few-shot examples, and measuring output consistency across models.
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
  --skill ai-evaluation \
  --skill ai-cost-optimization \
  --skill model-serving-production \
  --skill mcp-development \
  --skill multi-agent-orchestration \
  --skill fine-tuning \
  --skill llm-observability \
  --skill prompt-engineering \
  --skill ai-system-architecture \
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

## Recent Additions

| Skill | Added | Purpose |
|-------|-------|---------|
| `mcp-development` | 2026-07 | Build MCP servers for agent tool access |
| `multi-agent-orchestration` | 2026-07 | Orchestrate multi-agent workflows with subagent decomposition |
| `fine-tuning` | 2026-07 | Fine-tune LLMs with Axolotl, Unsloth, TRL or LLaMA-Factory |
| `llm-observability` | 2026-07 | Monitor, trace, and alert on LLM behavior in production |
| `prompt-engineering` | 2026-07 | Design, test, and version prompts systematically |
| `ai-system-architecture` | 2026-07 | Design, review and document AI system architecture end-to-end |
