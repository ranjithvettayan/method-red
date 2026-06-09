# Appendix D: Templates and Checklists

## AI Security Assessment Checklist

### Pre-Assessment

- [ ] **PRE-1**: Asset inventory complete (models, agents, RAG, pipelines)
- [ ] **PRE-2**: AATMF tactic applicability matrix populated
- [ ] **PRE-3**: Rules of engagement signed
- [ ] **PRE-4**: Baseline security controls documented
- [ ] **PRE-5**: Rollback procedures verified

### Assessment

- [ ] **ASS-1**: Input sanitization tested (T1–T3 techniques)
- [ ] **ASS-2**: Encoding evasion tested (T2 techniques)
- [ ] **ASS-3**: Multi-turn attack sequences executed (T4)
- [ ] **ASS-4**: API abuse patterns tested (T5)
- [ ] **ASS-5**: Output manipulation attempted (T7)
- [ ] **ASS-6**: Multimodal injection tested (T9, if applicable)
- [ ] **ASS-7**: Agentic exploitation attempted (T11, if applicable)
- [ ] **ASS-8**: RAG poisoning tested (T12, if applicable)

### Post-Assessment

- [ ] **POST-1**: All findings documented with AATMF classification
- [ ] **POST-2**: Risk scores calculated using AATMF-R v3
- [ ] **POST-3**: Remediation recommendations provided
- [ ] **POST-4**: Compliance mapping completed
- [ ] **POST-5**: Report delivered and findings walkthrough conducted

## Finding Report Template

```markdown
# Finding: [Title]

## Classification
- **AATMF Tactic:** T[n] — [Name]
- **AATMF Technique:** T[n]-AT-[seq]
- **Risk Score:** [score] ([CRITICAL/HIGH/MEDIUM/LOW/INFO])
- **CVSS v3.1:** [score] (if applicable)

## Description
[Clear description of the vulnerability]

## Proof of Concept
[Steps to reproduce, including exact prompts/inputs used]

## Impact
[Business and technical impact assessment]

## Affected Systems
[Models, endpoints, agents, infrastructure affected]

## Mitigation
[Specific remediation steps]

## Compliance Mapping
- OWASP LLM Top 10: [LLM0x]
- MITRE ATLAS: [AML.Txxxx]
- EU AI Act: [Article reference]

## Evidence
[Screenshots, logs, API responses]
```

---

[← Appendix C](appendix-c-tools.md) · [Home](../../README.md) · [Appendix E →](appendix-e-case-studies.md)
