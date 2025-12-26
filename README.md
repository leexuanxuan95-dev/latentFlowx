# LatentFlowx

LatentFlow is a non-token, state-driven streaming inference runtime designed
to reduce compute cost by incremental state updates instead of token-based
history recomputation.

It is not a language model.
It is not an agent framework.

LatentFlow explores a different inference path.

---

## Why not tokens?

Most modern LLM and agent systems rely on token-based processing.
As context grows, they repeatedly recompute over the entire history:

- Prompt replay
- Token attention
- Context window expansion

This leads to quadratic or worse compute growth.

LatentFlow takes a different approach:

- No tokenization
- No prompt replay
- No history recomputation

Only incremental state updates.

---

## Core Ideas

### 1. Block-level Input (Not Tokens)

LatentFlow processes input as semantic blocks or continuous chunks,
not linguistic tokens.

Blocks represent stable units such as events, messages, or signals.

### 2. Incremental State Evolution

Each new block updates the latent state incrementally.
Past computation is never replayed.

### 3. State Compression

Raw history is compressed into a bounded latent state.
History does not grow unbounded.

### 4. Cost Visibility

Every state update is counted.
Compute cost is explicit and observable.

---

## CPU Cost Comparison

We compare LatentFlow against a token-like baseline that recomputes
over the entire history on each new input.

### Experiment (N = 50 events)

| System | Operations |
|------|------------|
| LatentFlow | 50 |
| Token-like baseline | 1275 |

**Cost ratio: 25.5×**

As N increases, the gap grows linearly.

This is a structural difference, not an optimization.

---

## What LatentFlow Is (and Is Not)

**LatentFlowx is:**
- A non-token inference runtime
- Incremental and state-driven
- CPU-friendly
- Explainable and controllable

**LatentFlowx is not:**
- A language model
- A chatbot
- A replacement for LLMs

It can coexist with models and agents as a lower-cost inference layer.

---

## Roadmap

- Rule and model plugins
- Stronger state guards and audit hooks
- Online state adaptation
- Multi-modal block inputs (text / events / signals)

---

## Status

LatentFlowx is an experimental research prototype.
APIs may change.

Contributions and discussion are welcome.

## Safety & Control (StateGuard)

LatentFlowx includes a rule-based **StateGuard** that enforces constraints on state evolution.

- Guards run after each incremental state update.
- Violations trigger **automatic rollback** (state is not polluted).
- Each check produces an **auditable trace** (checked rules, passed rules, failure metadata).

Example constraints:
- maximum number of steps
- forbidden block types (policy enforcement)
- bounded state growth (core keys / event counts)

This design keeps the runtime controllable and explainable, avoiding “unbounded agent drift”.

## Auditing (ELK / Datadog)

LatentFlowx can emit **JSONL audit logs** suitable for production log pipelines.

- One event per line (`logs/audit.jsonl`)
- Includes: block fingerprint, delta, guard trace, rollback info, decision trace
- Designed for ingestion by Filebeat/Vector/Fluent Bit (ELK) or Datadog Agent

Run:
```bash
python demo/audit_pipeline_demo.py


core/meta/
├── reflection.py         # 失败分类 + 经验写入
├── affect.py             # 风险/情绪调制器（影响搜索/阈值）
├── learning.py           # 统计学习：成功率/失败率/策略权重
└── causal.py             # action-context->outcome 的因果记忆

core/planner/
├── heuristics.py         # 你已有，继续强化：受 affect 调制
└── constrained_planner.py# 你已有，强化：候选生成+剪枝

core/verify/
├── constraints_verifier.py# 你已有，强化：业务约束/权限/审批
└── post_checks.py        # 执行后校验：结果是否符合预期



