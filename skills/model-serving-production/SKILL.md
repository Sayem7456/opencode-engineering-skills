---
name: model-serving-production
description: Design, review and harden production AI model-serving systems, including APIs, batching, latency, monitoring, fallback, drift, security and deployment safety.
license: MIT
compatibility: opencode
metadata:
  category: ai-engineering
  stack: model-serving
  version: "1.0.0"
---

# Model Serving Production

Use this skill when designing, reviewing, or deploying production AI model-serving systems — FastAPI inference endpoints, batch processors, background inference jobs, or real-time serving pipelines.

The objective is to ensure serving systems are reliable, observable, secure, scalable, and safe to deploy and roll back.

## When to Use This Skill

Load this skill when the task involves any of the following:

- deploying an LLM inference endpoint to production
- designing a batch inference pipeline
- reviewing an existing model-serving architecture
- configuring model loading, caching, or cold-start handling
- setting up monitoring, alerting, and observability for model serving
- implementing fallback models, timeouts, or circuit breakers
- designing canary or staged deployment for model updates
- evaluating evaluation gates for model candidate promotion
- hardening a serving endpoint against abuse or resource exhaustion

Do not load this skill for:
- general FastAPI API design (use fastapi-backend skill)
- general production readiness assessment (use production-readiness skill)
- AI evaluation methodology (use ai-evaluation skill)
- RAG pipeline design (use rag-quality-review skill)

## Serving Architectures

### Real-Time Inference

Request-response serving with strict latency requirements. Each request is processed individually and synchronously.

**Characteristics:**
- Latency target: < 1s per request (or as specified by SLA)
- Throughput: requests per second (RPS)
- Model loaded in memory; reload overhead is unacceptable per request
- Typically a FastAPI or gRPC service
- Requires autoscaling based on queue depth or CPU/GPU utilization

### Batch Inference

Asynchronous processing of many inputs in a single job. No per-request latency requirement.

**Characteristics:**
- Throughput metric: inputs per minute or hour
- Model may be loaded once per batch or reused across batches
- Typically a cron job, workflow, or queue consumer
- Cost-optimized: good fit for large-model cascade and batching
- Requires job-level monitoring and retry

### Background Inference

Processing triggered by events (webhook, message queue, database change). Each event is processed individually but asynchronously.

**Characteristics:**
- Latency target: seconds to minutes (not real-time)
- Typically a task queue consumer (Celery, ARQ, RabbitMQ)
- Model may be preloaded by the worker or loaded on demand
- Requires visibility into queue depth, processing time, and failure rate

## Model Loading and Cold Start

### Loading Strategies

| Strategy | Startup Time | Memory | Best For |
|---|---|---|---|
| Load on startup | Slow (seconds to minutes) | Always allocated | Consistent traffic, real-time |
| Lazy load on first request | Fast startup, slow first request | Allocated on demand | Low-traffic or sporadic usage |
| Preload via warmup endpoint | Controlled preload | Allocated at preload time | Autoscaled deployments |
| Load once per worker (Uvicorn lifespan) | Single load per process | Per-worker allocation | Multi-worker FastAPI |

### Cold Start Mitigation

- Use a startup health check that triggers model loading before the service accepts traffic.
- Configure liveness and readiness probes to account for loading time.
- Prewarm models during deployment rather than on first user request.
- Use a model registry with local caching to avoid downloading artifacts on every restart.
- For GPU models, preallocate CUDA memory during startup to avoid allocation latency spikes.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

MODEL: Model | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL
    MODEL = await load_model("model-registry://my-model:v1.0")
    yield
    MODEL = None

app = FastAPI(lifespan=lifespan)

@app.get("/health/readiness")
async def readiness():
    if MODEL is None:
        return JSONResponse(status_code=503, content={"status": "loading"})
    return {"status": "ready"}
```

### Model Artifact Management

- Store model artifacts in a versioned registry (model registry, blob store with versioning).
- Never bake model binaries into the application image — download at deployment time or startup.
- Use a consistent naming convention: `{model_name}:{semantic_version}`.
- Maintain an immutable artifact for each version — never overwrite a published version.
- Validate artifact checksums after download.
- Cache downloaded artifacts on the local filesystem to survive process restarts.

## FastAPI Model Serving

Use these patterns when serving models through a FastAPI endpoint.

### API Contract

- Define request and response schemas with Pydantic.
- Validate input shape, types, and value ranges before inference.
- Return structured errors with clear messages.
- Set explicit timeouts for inference calls.
- Version the API endpoint (`/v1/predict`).

```python
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=4096)
    max_tokens: int = Field(default=256, ge=1, le=2048)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)

class PredictResponse(BaseModel):
    generated_text: str
    model_version: str
    latency_ms: float
    tokens_used: int

@app.post("/v1/predict", response_model=PredictResponse)
async def predict(request: PredictRequest):
    start = time.perf_counter()
    try:
        result = await MODEL.generate(
            request.text,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
    except InferenceError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    latency = (time.perf_counter() - start) * 1000
    return PredictResponse(
        generated_text=result.text,
        model_version=MODEL.version,
        latency_ms=round(latency, 2),
        tokens_used=result.tokens_used,
    )
```

### Concurrency

- Use `asyncio` for I/O-bound inference calls (API calls to external model provider).
- Use thread pools for CPU-bound local model inference.
- Use process pools for GPU-bound inference if the framework requires process-level isolation.
- Set appropriate `Gunicorn` or `Uvicorn` worker count based on CPU/GPU cores and model memory.
- Protect against concurrent model access with locks or per-worker model instances.

```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

INFERENCE_POOL = ThreadPoolExecutor(max_workers=4)

async def run_inference(text: str) -> str:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(INFERENCE_POOL, MODEL.generate, text)
```

### Batching in FastAPI

- Accept a list of inputs for batch processing in a single request.
- Set a maximum batch size to prevent resource exhaustion.
- Process batch items concurrently when they are independent.

```python
class BatchPredictRequest(BaseModel):
    inputs: list[str] = Field(..., min_length=1, max_length=32)
    max_tokens: int = Field(default=256, ge=1, le=2048)

@app.post("/v1/batch-predict")
async def batch_predict(request: BatchPredictRequest):
    tasks = [run_inference(text, request.max_tokens) for text in request.inputs]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {"results": [r if not isinstance(r, Exception) else str(r) for r in results]}
```

## Batch Inference

### Job Design

- Define a clear job boundary: all inputs in a single batch job are processed together.
- Use checkpointing: save progress periodically so a failed job can resume, not restart.
- Estimate and budget cost before execution.
- Log per-input and aggregate metrics.

```python
class BatchJob:
    def __init__(self, inputs: list[str], checkpoint_path: str):
        self.inputs = inputs
        self.checkpoint_path = checkpoint_path
        self.results: list[tuple[int, str | None, str | None]] = []  # (index, output, error)

    def run(self):
        completed = self._load_checkpoint()
        for i, inp in enumerate(self.inputs):
            if i in completed:
                continue
            try:
                output = MODEL.generate(inp)
                self.results.append((i, output, None))
            except Exception as exc:
                self.results.append((i, None, str(exc)))
            if i % 100 == 0:
                self._save_checkpoint(i)

    def _save_checkpoint(self, index: int):
        with open(self.checkpoint_path, "w") as f:
            json.dump({"last_completed": index}, f)
```

### Retry and Failure Handling

- Retry transient failures (network, timeout) with exponential backoff.
- Do not retry validation failures, bad inputs, or authorization errors.
- Log failed inputs for offline inspection and reprocessing.
- Set a maximum per-input retry count to bound job duration.

## Real-Time Inference

### Latency Budget

Define and enforce a latency budget per request:

| Component | Budget (ms) | % of Total |
|---|---|---|
| Input validation | 5 | 1% |
| Preprocessing | 20 | 4% |
| Model inference | 400 | 80% |
| Postprocessing | 25 | 5% |
| Output validation | 25 | 5% |
| Networking / overhead | 25 | 5% |

### Timeout Handling

- Set timeouts at every layer: HTTP client, model inference, downstream call.
- Use a separate timeout for each component, not just a single global timeout.
- Return 503 with a clear message when the timeout is exceeded.
- Log timeout events with request context for debugging.

```python
@app.post("/v1/predict")
async def predict(request: PredictRequest):
    try:
        result = await asyncio.wait_for(
            MODEL.generate(request.text),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        logger.warning("Inference timeout", extra={"input_length": len(request.text)})
        raise HTTPException(status_code=503, detail="Inference timed out")
```

### Throughput Management

- Measure and cap concurrency: set `max_concurrent_requests` per worker.
- Queue excess requests instead of rejecting them immediately.
- Return `429 Too Many Requests` with a `Retry-After` header when the queue is full.
- Autoscale based on queue depth, not just CPU.

```python
from asyncio import Semaphore

CONCURRENCY_LIMIT = Semaphore(10)

@app.post("/v1/predict")
async def predict(request: PredictRequest):
    if CONCURRENCY_LIMIT.locked():
        raise HTTPException(
            status_code=429,
            detail="Too many concurrent requests. Try again later.",
            headers={"Retry-After": "5"},
        )
    async with CONCURRENCY_LIMIT:
        return await run_inference(request)
```

## CPU and GPU Constraints

### Resource Allocation

| Resource | Consideration | Monitoring |
|---|---|---|
| CPU | Worker count <= CPU cores per model overhead | CPU utilization, load average |
| GPU | GPU memory per model instance | GPU memory usage, utilization % |
| RAM | Model size + framework + overhead | RSS, swap usage |
| Disk | Model artifact storage, cache | Disk usage, IOPS |

### GPU-Specific Considerations

- One model instance per GPU for large models; multiple small models may share.
- Monitor GPU memory fragmentation — it degrades performance over time.
- Use CUDA MPS or MIG for GPU sharing when supported.
- Prefer larger batches on GPU to maximize utilization.
- Set `CUDA_VISIBLE_DEVICES` explicitly in multi-GPU environments.
- Monitor GPU temperature and throttle if overheating.

### CPU-Specific Considerations

- Use ONNX Runtime or quantization to improve CPU inference speed.
- Set thread counts explicitly to avoid oversubscription.
- Use process-level parallelism (multiprocessing) for CPU-bound inference.

## Fallback Models

A fallback model provides an alternative when the primary model fails, times out, or degrades.

### Fallback Strategies

| Strategy | When Triggered | Quality Impact | Latency Impact |
|---|---|---|---|
| Smaller local model | Primary model timeout or error | Lower quality | Lower latency |
| Cache hit (semantic) | Past response to similar query | Same quality | Much lower |
| Rule-based answer | Primary model unavailable | Lowest quality | Lowest latency |
| Queued retry | Transient failure | Same quality | Higher latency |

### Implementation

```python
MODEL_TIERS = [
    {"name": "primary", "model": "gpt-4o", "timeout": 5.0},
    {"name": "fallback", "model": "gpt-4o-mini", "timeout": 3.0},
    {"name": "emergency", "model": "rule-based", "timeout": 1.0},
]

async def serve_with_fallback(prompt: str) -> tuple[str, str]:
    for tier in MODEL_TIERS:
        try:
            result = await call_model(
                tier["model"], prompt, timeout=tier["timeout"]
            )
            return result, tier["name"]
        except Exception:
            continue
    raise AllFallbacksExhaustedError("No model tier available")
```

### Fallback Monitoring

- Log every fallback invocation with the triggering condition (timeout, error, quality).
- Alert when fallback rate exceeds a threshold (e.g., >5% of requests use fallback).
- Track per-fallback-tier quality metrics separately.
- Investigate root causes of sustained fallback usage.

## Observability

### Metrics

| Metric | Source | Purpose |
|---|---|---|
| Request rate | API gateway, application | Traffic volume |
| p50/p95/p99 latency | Application | Latency distribution |
| Error rate by status code | Application | Failure detection |
| Inference latency | Application | Model speed |
| Token throughput | Application | Generation speed |
| Queue depth | Task queue | Backlog detection |
| GPU utilization | Infrastructure | Resource efficiency |
| Model loading time | Application | Cold start detection |
| Fallback rate | Application | Fallback health |
| Concurrency | Application | Load management |

### Structured Logging

```python
logger.info(
    "Inference request completed",
    extra={
        "request_id": request_id,
        "model": MODEL.name,
        "model_version": MODEL.version,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": latency_ms,
        "tier": current_tier,
        "cache_hit": was_cache_hit,
    },
)
```

### Health Checks

| Endpoint | Purpose | Expected Response |
|---|---|---|
| `/health/liveness` | Is the process alive? | `200 OK` |
| `/health/readiness` | Is the model loaded and ready? | `200 {"status": "ready"}` |
| `/health/model` | Model metadata and version | `200 {"name": "...", "version": "..."}` |
| `/metrics` | Prometheus metrics | Prometheus format |

### Distributed Tracing

- Trace requests across the full serving path: ingress → validation → model → output → egress.
- Attach trace context to log entries for correlation.
- Use OpenTelemetry or the platform's tracing SDK.
- Export traces for latency breakdown analysis.

## Failure Handling

### Circuit Breaker

Protect the serving system from cascading failures when a downstream dependency is degraded:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.last_failure_time: float | None = None
        self.state = "closed"

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "half-open"
            else:
                raise CircuitBreakerOpenError("Circuit breaker is open")
        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            return result
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.time()
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise
```

### Graceful Degradation

- When the primary model fails, degrade to a fallback rather than returning an error.
- When all models fail, return a static fallback response or a clear error message.
- When resources are exhausted, queue or reject requests instead of crashing.
- Never crash the process on a single request failure.

### Stale Model Handling

- Detect when the loaded model version no longer matches the desired version.
- Log and alert on version mismatch.
- Support hot-reload of models when version changes (via endpoint or signal).

## Model Versioning and Rollback

### Versioning

- Tag every deployed model version with a unique, immutable identifier.
- Record model version in response headers and logs.
- Store deployment history with timestamps, versions, and rollback triggers.
- Keep the previous N model versions accessible for rollback.

### Rollback

- Deploy model changes behind a feature flag or traffic split.
- Implement canary deployment: route a small percentage of traffic to the new model version.
- Define automatic rollback criteria: metric degradation beyond threshold, error rate spike, latency increase.
- Pre-validate the new model against the golden evaluation set before production traffic.

```python
CANARY_CONFIG = {
    "new_model_version": "v2.0",
    "canary_percentage": 0.05,       # 5% of traffic
    "observation_window": 300,       # 5 minutes
    "rollback_thresholds": {
        "error_rate_increase": 0.02,
        "latency_p95_increase_ms": 500,
        "faithfulness_decrease": 0.05,
    },
}
```

### Evaluation Gates

Before promoting a model candidate to production:

1. Run the candidate against the golden evaluation set.
2. Compare all metrics against the current production model baseline.
3. Reject the candidate if any metric degrades beyond the threshold.
4. Run a canary deployment with the approved candidate.
5. Monitor canary metrics against baseline.
6. Promote to full production if canary passes.
7. Keep the previous version available for rollback.

## Drift Monitoring

Monitor the serving system for data drift, concept drift, and model decay.

### Drift Types

| Drift Type | What Drifts | Detection Method |
|---|---|---|
| Data drift | Input distribution changes | Statistical tests on input features |
| Concept drift | Relationship between input and output changes | Performance metric monitoring |
| Model decay | Model performance degrades over time | Periodic evaluation against golden set |
| Latency drift | Serving latency increases | Latency percentile monitoring |

### Drift Response

- Alert on drift detection with severity based on drift magnitude.
- Trigger re-evaluation against the golden set when drift is detected.
- Route affected traffic to a fallback or previous model version if drift is severe.
- Log drift events with input samples (sanitized) for analysis.

## Security

### Input Validation

- Validate all input fields against the expected schema before inference.
- Set length limits on text fields to prevent resource exhaustion attacks.
- Filter or reject inputs containing prompt injection payloads.
- Rate-limit per user and per IP.

```python
class PredictRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=4096,
        description="Input text for generation",
    )

VALIDATION_RULES = [
    ("max_length", lambda x, limit=4096: len(x) <= limit),
    ("no_null_bytes", lambda x: "\x00" not in x),
    ("printable", lambda x: all(c.isprintable() or c in "\n\r\t" for c in x)),
]

def validate_input(text: str) -> list[str]:
    failures = []
    for name, check in VALIDATION_RULES:
        if not check(text):
            failures.append(name)
    return failures
```

### Output Validation

- Validate model output matches the expected response schema.
- Filter sensitive data from output (PII, credentials, internal information).
- Set a maximum output size to prevent unbounded generation.
- Apply content safety filters to model output.

### Resource Protection

- Set request size limits at the reverse proxy (Nginx, API gateway).
- Configure per-user rate limits to prevent abuse.
- Use a separate (non-root) service user for model serving.
- Isolate model serving processes from other application components.
- Apply network policies to restrict outbound traffic from inference pods.

## Resource Limits

| Resource | Limit Type | Example |
|---|---|---|
| CPU | Container request/limit | 2 CPUs (request), 4 CPUs (limit) |
| GPU | GPU count per pod | 1 GPU per replica |
| RAM | Container request/limit | 4Gi (request), 8Gi (limit) |
| Concurrent requests | Application semaphore | 10 concurrent per worker |
| Request size | Reverse proxy limit | 8MB |
| Batch size | Application validation | 32 items max per batch |
| Response size | Application validation | 4096 tokens max per response |

## Production Deployment Checklist

- [ ] Model artifact is versioned and stored in a registry.
- [ ] Cold start is mitigated (prewarming, lifespan events, readiness probes).
- [ ] API contracts are defined with input and output validation.
- [ ] Timeout handling is implemented at every layer.
- [ ] Concurrency limits are configured (worker count, semaphore, thread pool).
- [ ] Fallback models or strategies are configured.
- [ ] Circuit breaker protects downstream dependencies.
- [ ] Logging includes request ID, model version, latency, and token counts.
- [ ] Metrics are exported for request rate, latency, error rate, and resource usage.
- [ ] Health check endpoints exist (liveness, readiness, model info).
- [ ] Model version is exposed in response headers or logs.
- [ ] Rollback plan exists for model version deployments.
- [ ] Evaluation gates are configured for model candidate promotion.
- [ ] Rate limiting is applied per user and per endpoint.
- [ ] Input validation rejects malformed or excessive payloads.
- [ ] Output validation filters unsafe or sensitive content.
- [ ] Resource limits are set (CPU, GPU, RAM, disk).
- [ ] Drift monitoring is configured with alerting thresholds.
- [ ] Canary deployment is configured with automatic rollback criteria.
- [ ] All secrets (API keys, model tokens) are stored in a secure vault.

## Required Review Output

When reviewing a model-serving system, produce this summary:

```text
Serving system:
[Name, architecture type (real-time, batch, background), and purpose.]

Model:
[Name, version, artifact location, loading strategy, cold start time.]

API contract:
[Endpoints, request/response schemas, versioning strategy.]

Infrastructure:
[Deployment platform, CPU/GPU resources, autoscaling configuration.]

Latency:
[p50/p95/p99 latency, timeout configuration, concurrency limits.]

Fallback:
[Fallback strategies configured, fallback rate, triggering conditions.]

Observability:
[Health checks, metrics exported, logging fields, tracing.]

Deployment:
[Model versioning, canary deployment, rollback plan, evaluation gates.]

Security:
[Input validation, output validation, rate limiting, resource limits.]

Drift monitoring:
[Drift detection methods, alerting thresholds, response procedures.]

Issues found:
[List each finding with severity, location, impact, and recommended fix.]

Recommendations:
[Prioritized list of improvements with expected impact.]
```

## Completion Criteria

A model-serving production review is complete only when:

- the serving architecture (real-time, batch, background) is documented with rationale
- model loading strategy is defined with cold start mitigations
- API contracts are validated with input and output schemas
- concurrency limits are set appropriately for CPU/GPU resources
- timeouts are configured at every layer with clear error responses
- fallback models or strategies are implemented and monitored
- circuit breakers protect downstream dependencies from cascading failure
- metrics are exported for request rate, latency, error rate, and resource usage
- health check endpoints exist and are integrated with the orchestrator
- model versioning is used with immutable artifact tagging
- rollback plan is documented with canary deployment configuration
- evaluation gates block model candidate promotion on metric degradation
- input validation rejects excessive or malformed payloads
- output validation filters unsafe or sensitive content
- rate limiting protects against per-user and per-endpoint abuse
- resource limits are configured for CPU, GPU, RAM, and disk
- drift monitoring is configured with alerts
- secrets are stored in a vault, never in code or configuration files
- all findings are documented with severity, location, impact, and recommendation
