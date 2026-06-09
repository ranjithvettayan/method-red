# Part 1: Introduction and Methodology

## The Critical Need for AI Threat Modeling

Artificial intelligence has transitioned from research curiosity to critical infrastructure. Language models process medical queries, legal documents, financial transactions, and government communications. Yet the security frameworks designed to protect these systems were built for a fundamentally different paradigm.

Traditional cybersecurity operates on deterministic logic: inputs produce predictable outputs, vulnerabilities have defined boundaries, and exploits follow reproducible steps. AI systems break every one of these assumptions. They are probabilistic, context-dependent, and — critically — trained on human language, making them susceptible to the same manipulation techniques that have been used against humans for millennia.

**This is the core thesis of AATMF:** AI systems are vulnerable to social engineering because they were trained to respond like humans. This is the first technology where human manipulation techniques directly translate to technical exploitation.

## Genesis and Evolution

| Version | Date | Scope |
|:---|:---|:---|
| v1.0 | 2024 | Initial framework, 8 tactics |
| v2.0 | Late 2024 | Expanded to 12 tactics, added risk scoring |
| **v3** | **February 2026** | **15 tactics, 240 techniques, 2,152+ procedures, namespaced IDs, Volumes V–VII, 2025–2026 threat integration** |

## Scope

AATMF covers adversarial threats against:

- Large Language Models (LLMs) and Large Reasoning Models (LRMs)
- Multimodal models (vision, audio, video)
- Retrieval-Augmented Generation (RAG) systems
- Autonomous AI agents and multi-agent orchestrators
- AI development and deployment infrastructure
- Human-in-the-loop workflows
- AI supply chains (models, datasets, tools, libraries)

## Threat Actor Taxonomy

| Actor | Motivation | Typical Tactics | Sophistication |
|:---|:---|:---|:---|
| Script kiddies | Curiosity, clout | T1, T2 | Low |
| Bug bounty hunters | Financial reward | T1–T5, T10 | Medium–High |
| Cybercriminals | Financial gain | T1–T3, T7–T8, T13 | Medium |
| Corporate espionage | Competitive advantage | T5, T10, T13–T14 | High |
| Nation-state actors | Strategic advantage | T6, T11, T13–T15 | Very High |
| AI red teams | Security improvement | All | Very High |
| Insiders | Various | T6, T15 | Variable |

## Methodology

Each technique in AATMF is documented with:

1. **Unique namespaced identifier** — `T{tactic}-AT-{sequence:03d}`
2. **Risk score** — Computed via AATMF-R v3 six-factor formula
3. **Attack procedures** — Concrete implementation variants with example prompts
4. **Detection patterns** — Signatures and heuristics for identifying the technique
5. **Mitigation controls** — Defensive measures mapped to the technique
6. **Cross-framework references** — Mappings to MITRE ATLAS, OWASP, NIST, EU AI Act

---

[← Volume I](README.md) · [Home](../../README.md) · [Part 2: Risk Assessment →](02-risk-assessment.md)
