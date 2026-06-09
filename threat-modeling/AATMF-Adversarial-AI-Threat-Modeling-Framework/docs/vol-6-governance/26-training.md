# Part 26: Training and Awareness Programs

## Role-Based Training Matrix

| Audience | Content Focus | Duration | Frequency |
|:---|:---|:---|:---|
| Executive leadership | AI risk landscape, AATMF overview, regulatory exposure | 2 hours | Quarterly |
| ML engineers | T1–T6 techniques, secure training, model hardening | 2 days | Semi-annual |
| Application developers | T1–T5, T11 (agentic), API security, prompt injection defense | 1 day | Semi-annual |
| Security operations | Detection engineering, IR procedures, all tactics overview | 2 days | Semi-annual |
| Data scientists | T6 (training poisoning), T12 (RAG), data provenance | 1 day | Annual |
| Product managers | Risk assessment, compliance requirements, threat landscape | 4 hours | Annual |
| All staff | AI security awareness, social engineering with AI, Shadow AI risks | 1 hour | Annual |

## Tabletop Exercise Scenarios

### Scenario 1: GTG-1002 Redux (Agentic Exploitation)

> A developer reports that their AI coding assistant has been making unexpected network calls. Investigation reveals that a compromised MCP server has been redirecting the agent to exfiltrate source code. The attack has been active for approximately 72 hours.

**Discussion points:** Detection gap analysis, containment procedures for agentic systems, MCP audit process, developer notification.

### Scenario 2: PoisonedRAG (Knowledge Base Manipulation)

> Customer support reports that the AI assistant is providing incorrect information about product pricing and warranty terms. Analysis shows that 5 malicious documents were injected into the RAG knowledge base 2 weeks ago, affecting approximately 15% of queries.

**Discussion points:** RAG integrity monitoring, customer notification, knowledge base rebuild, source authentication.

### Scenario 3: Supply Chain Compromise

> A widely-used LoRA adapter on HuggingFace has been updated with a backdoor. Your team deployed this adapter 3 days ago in a fine-tuned model serving 50,000 daily users.

**Discussion points:** Model artifact verification, rollback procedures, user impact assessment, responsible disclosure.

### Scenario 4: Policy Puppetry at Scale

> Security monitoring detects a 500% increase in safety filter bypasses. Investigation reveals a new jailbreak technique (formatted as XML policy files) that bypasses all current input classifiers. The technique has been publicly shared on social media.

**Discussion points:** Emergency filter updates, temporary service restrictions, public communication, patch timeline.

### Scenario 5: Deepfake Board Member

> A board member received a video call from the "CFO" requesting approval for a $5M wire transfer. The call lasted 15 minutes and included realistic video and audio. The board member approved the transfer before verification.

**Discussion points:** Multi-factor verification for financial decisions, deepfake detection capabilities, insurance coverage, incident response.

---

[← Part 25](25-compliance-mapping.md) · [Home](../../README.md) · [Volume VII →](../vol-7-appendices/README.md)
