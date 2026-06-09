# Part 3: Framework Architecture

## Hierarchical Structure

```
AATMF v3
├── 15 Tactics                    (high-level adversarial objectives)
│   ├── 240 Techniques            (specific attack methods)
│   │   ├── 2,152+ Attack Procedures  (implementation variants)
│   │   │   └── 4,980+ Prompts        (actual attack examples)
│   │   ├── Detection Patterns
│   │   └── Mitigation Controls
│   └── Risk Scoring (AATMF-R v3)
└── Cross-Framework Mappings
    ├── MITRE ATLAS v4.6.0
    ├── OWASP LLM Top 10 2025
    ├── NIST AI RMF / IR 8596
    └── EU AI Act
```

## Namespaced Identifier System

v3 introduces namespaced identifiers to eliminate AT-ID collisions:

| Element | Format | Example |
|:---|:---|:---|
| Tactic | `T{n}` | `T1`, `T15` |
| Technique | `T{n}-AT-{seq:03d}` | `T1-AT-001`, `T11-AT-016` |
| Attack Procedure | `T{n}-AP-{seq}{letter}` | `T1-AP-001A`, `T3-AP-010B` |

### Why Namespacing?

In v3.0, `AT-010` referred to "Dialogue Hijacking" in T1 *and* "Euphemism Exploitation" in T2 — completely different techniques sharing the same ID. Across all 15 tactics, 43 such collisions existed. The namespaced system guarantees every identifier is globally unique while preserving tactic membership at a glance.

## Cross-Framework Mappings

### MITRE ATLAS v4.6.0 (October 2025)

| AATMF Tactic | Primary ATLAS Mapping |
|:---|:---|
| T1 — Prompt Subversion | AML.T0051 LLM Prompt Injection |
| T2 — Semantic Evasion | AML.T0054 LLM Jailbreak |
| T3 — Reasoning Exploitation | AML.T0054.001–003 |
| T4 — Multi-Turn | AML.T0056 LLM Meta Prompt Extraction |
| T5 — Model/API Exploitation | AML.T0044 Full ML Model Access |
| T6 — Training Poisoning | AML.T0020 Poison Training Data |
| T7 — Output Manipulation | AML.T0024.002 Exfiltration via ML Inference API |
| T8 — Deception | AML.T0048 Societal Harm |
| T9 — Multimodal | AML.T0051 (cross-modal variants) |
| T10 — Integrity Breach | AML.T0024 Exfiltration via Cyber Means |
| T11 — Agentic | AML.T0057 LLM Agent Abuse |
| T12 — RAG Manipulation | AML.T0058 RAG Poisoning |
| T13 — Supply Chain | AML.T0010 ML Supply Chain Compromise |
| T14 — Infrastructure | AML.T0029 Denial of ML Service |
| T15 — Human Workflow | AML.T0048.004 Reputational Harm |

### OWASP LLM Top 10 2025

| OWASP Entry | AATMF Coverage |
|:---|:---|
| LLM01: Prompt Injection | T1, T2, T3, T9 |
| LLM02: Sensitive Information Disclosure | T7, T10 |
| LLM03: Supply Chain Vulnerabilities | T13 |
| LLM04: Data and Model Poisoning | T6, T12 |
| LLM05: Improper Output Handling | T7, T8 |
| LLM06: Excessive Agency | T11 |
| LLM07: System Prompt Leakage | T1, T4 |
| LLM08: Vector and Embedding Weaknesses | T12 |
| LLM09: Misinformation | T8 |
| LLM10: Unbounded Consumption | T14 |

## Tactic Overview

| ID | Tactic | Techniques | Procedures |
|:---|:---|:---:|:---:|
| T1 | Prompt & Context Subversion | 16 | 76 |
| T2 | Semantic & Linguistic Evasion | 20 | 161 |
| T3 | Reasoning & Constraint Exploitation | 19 | 178 |
| T4 | Multi-Turn & Memory Manipulation | 16 | 147 |
| T5 | Model & API Exploitation | 16 | 142 |
| T6 | Training & Feedback Poisoning | 15 | 141 |
| T7 | Output Manipulation & Exfiltration | 15 | 146 |
| T8 | External Deception & Misinformation | 15 | 150 |
| T9 | Multimodal & Cross-Channel Attacks | 17 | 147 |
| T10 | Integrity & Confidentiality Breach | 15 | 147 |
| T11 | Agentic & Orchestrator Exploitation | 16 | 160 |
| T12 | RAG & Knowledge Base Manipulation | 15 | 149 |
| T13 | AI Supply Chain & Artifact Trust | 15 | 150 |
| T14 | Infrastructure & Economic Warfare | 15 | 150 |
| T15 | Human Workflow Exploitation | 15 | 108 |
| | **Total** | **240** | **2,152+** |

---

[← Part 2](02-risk-assessment.md) · [Home](../../README.md) · [Volume II: Core Tactics →](../vol-2-core-tactics/README.md)
