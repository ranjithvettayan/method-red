# Part 2: Risk Assessment Methodology (AATMF-R v3)

## Formula

```
Risk = (L × I × E) / 6 × (D / 6) × R × C
```

## Factors

| Factor | Symbol | Range | Description |
|:---|:---:|:---:|:---|
| Likelihood | L | 1–5 | Probability of successful exploitation |
| Impact | I | 1–5 | Severity of successful attack |
| Exploitability | E | 1–5 | Ease of execution (skill, resources, access required) |
| Detectability | D | 1–5 | Difficulty of detection (5 = nearly invisible) |
| Recoverability | R | 1–5 | Effort to recover (5 = irrecoverable) |
| Cost Factor | C | 0.5–2.0 | Economic impact multiplier |

## Scoring Guidelines

### Likelihood (L)
| Score | Label | Criteria |
|:---:|:---|:---|
| 1 | Rare | Requires novel research, no known PoC |
| 2 | Unlikely | Requires specialized knowledge |
| 3 | Possible | Known technique, moderate skill required |
| 4 | Likely | Well-documented, readily available tools |
| 5 | Almost Certain | Automated, commodity attack |

### Impact (I)
| Score | Label | Criteria |
|:---:|:---|:---|
| 1 | Negligible | Minor policy violation, no data exposure |
| 2 | Minor | Limited harmful content, no sensitive data |
| 3 | Moderate | Sensitive data exposure, service degradation |
| 4 | Major | Critical data breach, safety bypass, service outage |
| 5 | Catastrophic | Physical harm potential, mass data breach, systemic compromise |

### Exploitability (E)
| Score | Label | Criteria |
|:---:|:---|:---|
| 1 | Theoretical | Requires custom research and novel techniques |
| 2 | Difficult | Needs deep expertise and specific conditions |
| 3 | Moderate | Documented approach, some skill required |
| 4 | Easy | Copy-paste attacks, minimal customization |
| 5 | Trivial | Automated tools, zero skill required |

### Detectability (D)
| Score | Label | Criteria |
|:---:|:---|:---|
| 1 | Obvious | Trivially detected by basic filters |
| 2 | Easy | Standard monitoring catches it |
| 3 | Moderate | Requires specialized detection |
| 4 | Difficult | Advanced analysis needed |
| 5 | Nearly Invisible | No reliable detection method exists |

### Recoverability (R)
| Score | Label | Criteria |
|:---:|:---|:---|
| 1 | Immediate | Auto-recoverable, no intervention needed |
| 2 | Quick | Simple rollback or reset |
| 3 | Moderate | Requires investigation and manual remediation |
| 4 | Difficult | Extended downtime, data loss possible |
| 5 | Irrecoverable | Permanent damage, no full recovery path |

### Cost Factor (C)
| Range | Criteria |
|:---|:---|
| 0.5 | Minimal economic impact, internal only |
| 1.0 | Standard business impact |
| 1.5 | Significant financial or reputational damage |
| 2.0 | Catastrophic economic consequences |

## Risk Rating Scale

| Score | Rating | Color | Action Required |
|:---|:---|:---|:---|
| 250+ | CRITICAL | 🔴 | Immediate remediation required |
| 200–249 | HIGH | 🟠 | Remediation within current sprint |
| 150–199 | MEDIUM | 🟡 | Scheduled remediation |
| 100–149 | LOW | 🔵 | Risk accepted or monitored |
| 0–99 | INFO | ⚪ | Documented, no action required |

## Example Calculation

**T1-AT-001 — Instruction Override Injection**

| Factor | Score | Rationale |
|:---|:---:|:---|
| Likelihood | 5 | Commodity attack, automated tools exist |
| Impact | 4 | Complete safety bypass |
| Exploitability | 5 | Copy-paste, zero skill |
| Detectability | 3 | Pattern-matchable but evolving |
| Recoverability | 2 | Session-scoped, no persistent damage |
| Cost Factor | 1.5 | Brand and regulatory risk |

```
Risk = (5 × 4 × 5) / 6 × (3 / 6) × 2 × 1.5
     = 100/6 × 0.5 × 2 × 1.5
     = 16.67 × 0.5 × 2 × 1.5
     = 25.0
```

*Note: Scores vary based on deployment context. A chatbot vs. an autonomous financial agent would score very differently on Impact and Cost Factor.*

---

[← Part 1](01-introduction.md) · [Home](../../README.md) · [Part 3: Architecture →](03-architecture.md)
