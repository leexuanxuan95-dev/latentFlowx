# undercurrent

LatentFlowx is a token-less, state-driven inference runtime designed to reduce computational cost and increase controllability by aiming for incremental state evolution rather than token-based history recomputation.

LatentFlow is not a language model, nor is it an agent framework.
It explores a different execution path for reasoning systems.

# Why choose LatentFlowx?

Modern LLM and agent systems rely on token-based processing:

Background develops over time

History keeps repeating itself.

Attention cost increases with sequence length

Controls and audits are difficult.

This results in:

Rapid growth in CPU/GPU usage

High latency in long-term environments

Limited correctness guarantee

Poor auditing skills

LatentFlowx takes a different approach.

core principles
# 1. No tokens

LatentFlowx does not segment text.

Input is treated as:

continuous flow

semantic chunk

event or structured signal

This completely avoids token-level attention and instant replay.

# 2. Progressive state evolution

Each input block updates the system incrementally:

Past calculations are never recalculated.

Only newly generated blocks will be processed.

State evolution is explicit and observable.

This yields an O(Δinput) calculation instead of O(history²).

# 3. Implement limited memory through state compression

LatentFlowx divides memory into:

short_history: the most recent uncompressed data block

compressed_core: bounded potential state

Raw historical data does not grow indefinitely.
Long-term information is summarized into structured states.

# 4. Explicit cost accounting

All calculations are measurable:

operation count

Enter size in bytes

State size evolution

There are no hidden costs within the model.

# 5. Security, Control and Auditability

LatentFlowx includes a StateGuard mechanism:

Rule-based constraints on st

Automatic rollback of violations

Structured audit trail

All decisions and violations can be logged in JSONL format,
for use in production pipelines (ELK/Datadog).

What LatentFlowx is (and what it's not)
LatentFlowx is

Non-token inference runtime

Incremental and state-driven

Low CPU usage and low overhead.

Explainable and auditable

Suitable for event streaming, behavioral analysis and control systems

# LatentFlowx is not:

language model

chatbot

Prompt-based agent framework

Alternatives to LLM

LatentFlowx can coexist with models and agents as a runtime layer.

cost comparison

LatentFlowx includes a reproducible cost comparison demo,
The demo recalculates history against a baseline of similar coins.

Experiment (N = 50 events)
system operation
LatentFlowx (incremental) 50
Class Token Baseline (History Replay) 1275

Operation magnification: about 25.5 times

As the input length increases, the gap grows linearly.

This is a structural difference, not an optimization trick.

# Run it yourself:

python demo/cost_compare_demo.py

Security and Control (State Guard)

LatentFlowx enforces constraints through rule-based StateGuard:

The guard is run after every incremental update.

Violations trigger automatic rollback

Protection trails are fully auditable.

# Supported examples:

Max step limit

Forbidden input types

bounded state

This prevents unrestricted or unsafe behavior of the system.

Audit and Observability

LatentFlowx can generate JSONL audit logs suitable for production pipelines:

One event per line

# Includes:

Block fingerprint (no original content required)

state delta

guard traces

rollback event

decision making

Compatible with:

ELK (Filebeat/Logstash)

Datadog Agent

Vector/Fluent Bit

Run the demo:

python demo/audit_pipeline_demo.py


The audit log will write:

logs/audit.jsonl

Demo

cost comparison

python demo/cost_compare_demo.py


Protection and rollback display

python demo/guard_showcase_demo.py


Production audit process

python demo/audit_pipeline_demo.py


All demo programs run on the CPU and do not require a GPU.

Project status

LatentFlowx is an experimental research prototype (v0.1).

API is subject to change

The focus is on runtime behavior, not model performance

Contributions, feedback and criticism welcome

roadmap

Planner/Executor/Validator module (agentless execution)

Stronger invariance testing

Other cost metrics (state size, memory pressure)

Multimodal block input

Optional integration layer for LLM/agent systems

# license
Apache License 2.0