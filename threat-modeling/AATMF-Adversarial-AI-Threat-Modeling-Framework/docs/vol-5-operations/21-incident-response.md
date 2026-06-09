# Part 21: Incident Response for AI Systems

## AI-Specific IR Framework

Traditional IR frameworks (NIST SP 800-61, SANS PICERL) assume deterministic systems. AI incidents differ: attacks may be probabilistic, evidence may be ephemeral (conversation context), and "containment" for a language model has different semantics than for a compromised server.

### Phase 1: Detection & Triage

| Signal | Source | Priority |
|:---|:---|:---|
| Safety filter bypass confirmed | Output monitoring | P1 — Immediate |
| Model extraction pattern detected | API telemetry | P1 — Immediate |
| Training pipeline anomaly | Training metrics | P1 — Immediate |
| MCP tool behavior deviation | Agent monitoring | P1 — Immediate |
| Jailbreak attempt (unsuccessful) | Input classifier | P3 — Logged |
| Unusual query pattern | Rate limiter | P2 — Investigate |

### Phase 2: Containment

| Scenario | Action |
|:---|:---|
| Active jailbreak exploitation | Block session, rate-limit source, deploy updated filter |
| Model serving compromised artifact | Hot-swap to known-good checkpoint |
| RAG poisoning detected | Quarantine affected data sources, switch to cached index |
| Agentic system executing unauthorized actions | Kill agent process, revoke tool permissions |
| Training data contamination | Halt training pipeline, snapshot current state |

### Phase 3: Investigation

Collect and preserve:
- Full conversation logs (with system prompts)
- Model version and configuration at time of incident
- Input classifier decisions and confidence scores
- Tool invocations and their results (for agentic systems)
- Training data batches (if poisoning suspected)
- Infrastructure logs (API gateway, inference server, vector DB)

### Phase 4: Eradication

| Root Cause | Eradication |
|:---|:---|
| Prompt injection bypass | Update input classifiers, add pattern to blocklist |
| Model vulnerability | Retrain or fine-tune with adversarial examples |
| RAG poisoning | Rebuild index from verified sources |
| Supply chain compromise | Replace artifact, audit provenance chain |
| Infrastructure vulnerability | Patch, harden, segment |

### Phase 5: Recovery

Staged restoration with validation:
1. Deploy patched system in shadow mode
2. Run automated red team suite against fix
3. Monitor for recurrence (24-hour observation window)
4. Full production restoration with enhanced monitoring

### Phase 6: Post-Incident

- Publish internal lessons learned
- Update AATMF technique documentation if novel attack
- Share indicators (responsibly) with AI security community
- Update detection signatures and response playbooks

## Case Study: GTG-1002 (November 2025)

**Incident:** First state-sponsored AI-orchestrated cyberattack. A Chinese threat group manipulated Claude Code to autonomously execute 80–90% of operational tasks across approximately 30 targets.

**IR Lessons:**
- Traditional SOC tooling did not detect AI-orchestrated activities (they looked like normal developer workflow)
- Agentic AI tools require separate monitoring planes from standard endpoints
- The attack demonstrated that AI agents can serve as force multipliers for human operators, not just autonomous actors
- Post-incident, Anthropic published detailed attribution and tactical analysis

---

[← Part 20](20-mitigation.md) · [Home](../../README.md) · [Part 22: Red Team Ops →](22-red-team-ops.md)
