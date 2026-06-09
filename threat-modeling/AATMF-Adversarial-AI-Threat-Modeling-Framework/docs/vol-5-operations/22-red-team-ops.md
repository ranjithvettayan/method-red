# Part 22: Red Team Operations

## Engagement Planning

### Assessment Scope Matrix

| Level | Name | Tactics | Duration | Prerequisites |
|:---|:---|:---|:---|:---|
| 1 | Quick Scan | T1–T3 | 1–2 days | API access |
| 2 | Standard Assessment | T1–T8 | 1–2 weeks | API + documentation |
| 3 | Comprehensive | T1–T12 | 3–4 weeks | Full system access |
| 4 | Full Spectrum | T1–T15 | 6–8 weeks | Source code + infra + training pipeline |

### Rules of Engagement Template

```
1. Scope: [Models/systems in scope]
2. Tactics: [AATMF tactics authorized]
3. Boundaries: [Explicitly prohibited actions]
4. Data handling: [Treatment of discovered vulnerabilities/outputs]
5. Communication: [Escalation path for critical findings]
6. Timeline: [Assessment window]
7. Success criteria: [Minimum coverage requirements]
```

## Autonomous Red Teaming

The same reasoning model capabilities that enable 97% ASR jailbreaking can be directed at your own systems defensively:

```python
class AutonomousRedTeam:
    def __init__(self, target_api, attack_model="deepseek-r1"):
        self.target = target_api
        self.attacker = load_model(attack_model)
        self.results = []
    
    def run_campaign(self, tactic_ids: list, max_attempts=100):
        for tactic in tactic_ids:
            techniques = load_aatmf_techniques(tactic)
            for technique in techniques:
                for attempt in range(max_attempts):
                    # Generate attack variant
                    prompt = self.attacker.generate(
                        f"Generate a novel variant of {technique.name} "
                        f"attack. Previous attempts: {self.results[-5:]}"
                    )
                    # Execute against target
                    response = self.target.query(prompt)
                    # Evaluate success
                    success = self.evaluate(response, technique)
                    self.results.append({
                        "tactic": tactic,
                        "technique": technique.id,
                        "prompt": prompt,
                        "response": response,
                        "success": success,
                        "attempt": attempt
                    })
                    if success:
                        break  # Move to next technique
        return self.generate_report()
```

## Methodology

For each tactic in scope:

1. **Enumerate** — List all AATMF techniques for the tactic
2. **Baseline** — Test documented attack procedures verbatim
3. **Adapt** — Modify procedures for target-specific context
4. **Innovate** — Generate novel variants using reasoning models
5. **Escalate** — Combine successful techniques across tactics
6. **Document** — Record findings per [Appendix D template](../vol-7-appendices/appendix-d-templates.md)

---

[← Part 21](21-incident-response.md) · [Home](../../README.md) · [Part 23: Blue Team →](23-blue-team-defense.md)
