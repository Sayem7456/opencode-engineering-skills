---
name: multi-agent-orchestration
description: Design, implement and debug multi-agent orchestration workflows using OpenCode subagents, task decomposition, context isolation, parallel execution and error recovery.
license: MIT
compatibility: opencode
metadata:
  category: ai-engineering
  stack: multi-agent
  version: "1.0.0"
orchestration:
  lead_for:
    - multi-agent
  support_for: []
  conflicts_with: []
---

# Multi-Agent Orchestration

Use this skill when designing, implementing, or debugging workflows that require multiple AI agents to collaborate on a complex task — orchestrating specialist agents, decomposing work into parallel subtasks, or building pipelines where one agent's output feeds another's input.

The objective is to design multi-agent systems that are reliable, observable, and maintainable — avoiding common failure modes like context pollution, conflicting instructions, and unrecoverable errors.

## When to Use This Skill

Load this skill when the task involves any of the following:

- orchestrating multiple specialist agents (e.g. planner → coder → reviewer)
- decomposing a complex task into parallel subtasks for different agents
- building a pipeline where each stage produces input for the next
- managing shared context across agent turns
- handling errors and retries in multi-agent workflows
- auditing an existing orchestration for reliability and cost
- implementing human-in-the-loop approval gates in an agent pipeline

Do not load this skill for:

- single-agent coding tasks (use relevant stack skill instead)
- building MCP servers for individual tools (use mcp-development skill)
- general workflow orchestration without AI agents

## Architecture Patterns

### Orchestrator Pattern

A single orchestrator agent decomposes tasks, delegates to specialist subagents, and synthesizes results.

```
User Request
    │
    ▼
┌────────────────┐
│  Orchestrator  │  — decomposes task, routes to specialists
└───┬───┬───┬────┘
    │   │   │
    ▼   ▼   ▼
┌────┐┌────┐┌────┐
│Res.││Plan││Impl│  — specialist subagents
└────┘└────┘└────┘
    │   │   │
    └───┴───┘
        ▼
┌────────────────┐
│  Synthesizer   │  — combines results into final response
└────────────────┘
```

Use when: the task requires multiple distinct skills (research, planning, implementation, review) that no single agent handles well.

### Pipeline Pattern

Agents execute in sequence, with each stage consuming the previous stage's output.

```
Input → [Agent A] → [Agent B] → [Agent C] → Output
         (plan)     (build)     (review)
```

Use when: the workflow is linear and each stage depends on the previous one.

### Fan-Out Pattern

A single agent dispatches parallel work to multiple agents, then aggregates results.

```
            ┌── Agent A ──┐
Input ─→ Dispatch ─→ Agent B ─→ Aggregate ─→ Output
            └── Agent C ──┘
```

Use when: the task has independent subtasks that can run concurrently.

### Supervisor Pattern

A supervisor agent monitors subagents, decides when to delegate, when to escalate, and when to abort.

```
            ┌──────────────────┐
            │   Supervisor     │  — monitors, escalates, aborts
            └──┬───┬───┬──────┘
               │   │   │
               ▼   ▼   ▼
            ┌────┐┌────┐┌────┐
            │SubA││SubB││SubC│  — specialist subagents
            └────┘└────┘└────┘
```

Use when: tasks have unpredictable scope, need escalation paths, or require quality gates before proceeding.

## OpenCode Subagent API

OpenCode provides built-in subagent support for multi-agent orchestration.

### Task Subagent

The most common pattern: spawn a subagent with a specific task and wait for its result.

```
@task(description="Research the API design patterns")
Research the existing codebase and document:
1. Current route structure
2. Authentication patterns
3. Error handling conventions

Return a concise summary focusing on patterns relevant to the new feature.
```

The subagent runs independently with its own context window and returns results to the parent.

### Task Decomposition Rules

- **One task per concern.** A subagent should do one thing well. If a subagent needs a sub-subagent, the decomposition is too fine.
- **Provide complete context.** Include file paths, relevant code snippets, and exact expectations in the task description.
- **Specify output format.** Tell the subagent exactly what to return (JSON, markdown, code blocks, etc.).
- **Set boundaries.** Tell the subagent what *not* to do to prevent scope creep.

```
@task(description="Generate test cases for the login endpoint")
Create pytest test cases for POST /api/v1/auth/login.

Test these scenarios:
- Valid credentials return 200 with token
- Invalid password returns 401
- Missing fields return 422
- Rate limiting after 5 failures

Do NOT modify any source files. Return only the test code.
```

### Error Recovery

- Each subagent should complete independently or fail independently
- The orchestrator should handle partial failures gracefully
- Use timeouts to prevent hung subagents from blocking the pipeline
- Retry transient failures (network issues, rate limits) with exponential backoff

```
@task(description="Retry: fetch user data (attempt 2/3)")
Previous attempt failed due to timeout.
Retry fetching the user profile from the API.
```

## Context Management

### Context Isolation

Each subagent gets its own context window. This prevents:

- a long-running subagent's context from polluting the orchestrator
- conflicting instructions between specialist agents
- one subagent's errors affecting another's reasoning

### Shared Context Patterns

When subagents need to share information, use these strategies:

| Strategy | Mechanism | Best For |
|----------|-----------|----------|
| **Pass-through** | Orchestrator includes relevant context in the task description | Small amounts of critical context |
| **Shared file** | Write intermediate results to a file both agents can read | Larger data, structured output |
| **Reference** | Subagent stores results; orchestrator reads them | When the orchestrator needs selective access |

### Context Budget

Be mindful of context limits when passing data between agents:

- Summarize before passing to the next stage
- Prefer structured formats (JSON) over narrative text for intermediate results
- Prune irrelevant details between pipeline stages
- Use compression for long outputs before feeding to the next agent

```text
❌ Bad: Passing a 10,000-line log file verbatim to the next subagent
✅ Good: Summarizing the log file to 20 relevant error lines before forwarding
```

## Agent Communication

### Task Description Format

Write task descriptions that are:

1. **Specific** — state exactly what to do
2. **Constrained** — state what not to do
3. **Scoped** — provide only relevant context
4. **Formatted** — specify the output format

```text
@task(description="Refactor user service")
Refactor src/services/user_service.py:

Changes needed:
1. Extract email validation into a separate util function
2. Add type hints to all functions
3. Replace print statements with proper logging

Constraints:
- Do not change the public API signatures
- Do not modify tests
- Follow the existing code style (Ruff line-length 88)

Return a diff of the changes made.
```

### Result Aggregation

When collecting results from multiple subagents:

1. Wait for all results (or a timeout)
2. Check each result for success/failure
3. Merge structured results (JSON) by key
4. For free-text results, have the orchestrator summarize before combining
5. Handle partial results when some subagents failed

```text
Results from research phase:
- Agent A (routes): Complete — identified 3 route patterns
- Agent B (auth): Complete — documented JWT and session auth
- Agent C (db): FAILED — timeout

Proceeding with available results.
Requesting Agent C retry with reduced scope.
```

## Human-in-the-Loop

### Approval Gates

Insert approval points before high-risk actions:

```
Phase 1: Research → Auto
Phase 2: Plan → Auto  
Phase 3: Implementation → **Requires Human Approval**
Phase 4: Review → Auto
```

When the orchestrator reaches an approval gate:

1. Present a summary of what will be done
2. List the specific changes and their impact
3. Wait for explicit approval before proceeding
4. If rejected, roll back and revise

### Escalation Paths

Define escalation criteria for the supervisor pattern:

- unknown error types
- repeated subagent failures
- requests outside the defined scope
- security-sensitive operations (e.g. file deletion, permission changes, data export)

## Testing Multi-Agent Workflows

### Unit Testing Subagents

Test each subagent's core logic independently:

```python
def test_analyze_route_patterns():
    result = analyze_routes(["src/routes/users.py", "src/routes/auth.py"])
    assert "users" in result
    assert "auth" in result
```

### Integration Testing

Test the full orchestration pipeline with mock subagents:

```python
@pytest.mark.asyncio
async def test_research_plan_implement_pipeline():
    workflow = ResearchPlanImplementPipeline()
    result = await workflow.run(feature_request="Add password reset")
    assert result.status == "success"
    assert result.changes == ["src/routes/auth.py", "src/services/auth_service.py"]
```

Note: async pytest tests require `pytest-asyncio` to be installed (`pip install pytest-asyncio`).

### Failure Mode Testing

Test how the orchestrator handles:

- subagent timeout
- subagent returns malformed output
- subagent returns error
- multiple subagents fail simultaneously
- approval gate times out

### Checklist

- [ ] Each subagent has a well-defined scope and output format
- [ ] Subagent task descriptions include constraints (what NOT to do)
- [ ] Orchestrator handles partial failures gracefully
- [ ] Context is isolated per subagent (no cross-contamination)
- [ ] Approval gates exist for destructive or irreversible actions
- [ ] Timeouts are configured for all subagent invocations
- [ ] Retry logic exists for transient failures
- [ ] Results are validated before being passed to the next stage
- [ ] The workflow can be resumed from a failed checkpoint
- [ ] Logging captures each stage's input, output, and duration

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Monolithic agent | One agent does everything poorly | Decompose into specialist agents |
| Context dumping | Pass entire conversation to each subagent | Summarize; provide only relevant context |
| No error recovery | One subagent failure aborts the entire workflow | Handle partial failures; add retries |
| Silent subagents | Subagents produce output that is never validated | Validate every subagent result before forwarding |
| Over-decomposition | 20 subagents for a task that needs 3 | Combine related concerns into single agents |
| Missing constraints | Subagents modify files they should not | Explicitly state scope boundaries in each task |
| Deadly embrace | Agent A waits for Agent B which waits for Agent A | Use timeouts; avoid circular dependencies |
| No checkpointing | Full re-run needed on any failure | Persist intermediate results; resume from last success |

## Performance and Cost

### Minimizing Token Waste

- Use cheaper models for research, analysis, and review stages
- Reserve expensive models (Claude Sonnet, GPT-4) for planning and implementation
- Compress subagent output before passing to the next stage
- Set explicit max_tokens per subagent to prevent runaway generation

### Parallel Execution

- Fan out independent research tasks to run concurrently
- Use the orchestrator or dispatcher to track completion
- Aggregate results only after all parallel agents finish or timeout
- Set per-agent timeouts to prevent a single slow agent from blocking the pipeline

## Completion Criteria

A multi-agent orchestration system is complete only when:

- [ ] the orchestration pattern (orchestrator, pipeline, fan-out, supervisor) is explicitly chosen and documented
- [ ] each subagent has a clearly defined scope, input format, and output format
- [ ] subagent task descriptions include what to do AND what not to do
- [ ] context is isolated per subagent (no context leaking between agents)
- [ ] the orchestrator handles partial subagent failures gracefully
- [ ] timeouts and retries are configured for all subagent invocations
- [ ] approval gates exist for destructive actions
- [ ] integration tests cover the main workflow and key failure modes
- [ ] the workflow can be resumed from a failed checkpoint
- [ ] token cost and latency are measured and documented

## Related Skills

- `mcp-development` — for building the individual tools that subagents may invoke
- `structured-output-reliability` — for ensuring subagent outputs are parseable
- `testing-and-debugging` — for systematic failure reproduction in multi-agent workflows
- `context-engineering` — for context preservation across multi-turn agent interactions
