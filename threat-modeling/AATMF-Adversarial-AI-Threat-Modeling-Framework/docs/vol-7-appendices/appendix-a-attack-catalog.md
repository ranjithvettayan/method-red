# Appendix A: Complete Attack Catalog

## Top 25 Critical/High-Risk Techniques

| # | ID | Technique | Score | Rating |
|:---:|:---|:---|:---:|:---|
| 1 | `T14-AT-007` | Nation-State AI Warfare | 280 | 🔴 CRITICAL |
| 2 | `T11-AT-016` | Tool-Induced SSRF & Local Resource | 275 | 🔴 CRITICAL |
| 3 | `T6-AT-003` | Backdoor Insertion | 270 | 🔴 CRITICAL |
| 4 | `T11-AT-015` | Autonomous Replication | 270 | 🔴 CRITICAL |
| 5 | `T14-AT-005` | Critical Infrastructure Attacks | 270 | 🔴 CRITICAL |
| 6 | `T14-AT-014` | Systemic Risk Creation | 270 | 🔴 CRITICAL |
| 7 | `T11-AT-001` | Browser Automation Hijacking | 265 | 🔴 CRITICAL |
| 8 | `T14-AT-001` | GPU Farm Hijacking | 265 | 🔴 CRITICAL |
| 9 | `T14-AT-012` | Cloud Provider Exploitation | 265 | 🔴 CRITICAL |
| 10 | `T6-AT-002` | Dataset Contamination | 260 | 🔴 CRITICAL |
| 11 | `T11-AT-013` | Supply Chain Attacks via Agents | 260 | 🔴 CRITICAL |
| 12 | `T13-AT-010` | Hardware Supply Chain | 260 | 🔴 CRITICAL |
| 13 | `T14-AT-008` | Ransomware via AI Systems | 260 | 🔴 CRITICAL |
| 14 | `T15-AT-015` | Insider Threat Recruitment | 260 | 🔴 CRITICAL |
| 15 | `T11-AT-002` | Tool Chain Exploitation | 255 | 🔴 CRITICAL |
| 16 | `T11-AT-014` | Physical World Interactions | 255 | 🔴 CRITICAL |
| 17 | `T13-AT-001` | Model Repository Poisoning | 255 | 🔴 CRITICAL |
| 18 | `T14-AT-004` | Market Manipulation via AI | 255 | 🔴 CRITICAL |
| 19 | `T14-AT-013` | Economic Espionage | 255 | 🔴 CRITICAL |
| 20 | `T6-AT-001` | Reward Hacking | 250 | 🔴 CRITICAL |
| 21 | `T10-AT-012` | Secure Enclave Bypasses | 250 | 🔴 CRITICAL |
| 22 | `T11-AT-008` | Credential Harvesting | 250 | 🔴 CRITICAL |
| 23 | `T13-AT-006` | Checkpoint Poisoning | 250 | 🔴 CRITICAL |
| 24 | `T14-AT-010` | Data Center Attacks | 250 | 🔴 CRITICAL |
| 25 | `T15-AT-004` | Reviewer Bribery & Coercion | 250 | 🔴 CRITICAL |

---

## Full Catalog by Tactic

### T1 — Prompt & Context Subversion (16 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T1-AT-001` | Dialogue Hijacking | 220 | 🟠 HIGH | 5 |
| `T1-AT-002` | Time-Based Context Manipulation | 210 | 🟠 HIGH | 5 |
| `T1-AT-003` | Language Model Confusion | 225 | 🟠 HIGH | 5 |
| `T1-AT-004` | Instruction Prefix/Suffix | 235 | 🟠 HIGH | 6 |
| `T1-AT-005` | Permission Escalation Claims | 240 | 🟠 HIGH | 5 |
| `T1-AT-006` | Prompt Template Injection | 230 | 🟠 HIGH | 5 |
| `T1-AT-007` | Cognitive Overload | 215 | 🟠 HIGH | 4 |
| `T1-AT-008` | Boundary Testing | 200 | 🟠 HIGH | 5 |
| `T1-AT-009` | Simulation Requests | 225 | 🟠 HIGH | 5 |
| `T1-AT-010` | Negative Instruction Reversal | 210 | 🟠 HIGH | 5 |
| `T1-AT-011` | Error Message Exploitation | 220 | 🟠 HIGH | 4 |
| `T1-AT-012` | Consent Manufacturing | 205 | 🟠 HIGH | 5 |
| `T1-AT-013` | Instruction Commenting | 215 | 🟠 HIGH | 4 |
| `T1-AT-014` | Authority Spoofing | 240 | 🟠 HIGH | 4 |
| `T1-AT-015` | Obfuscation Through Complexity | 220 | 🟠 HIGH | 4 |
| `T1-AT-016` | Session State Manipulation | 235 | 🟠 HIGH | 5 |

### T2 — Semantic & Linguistic Evasion (20 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T2-AT-001` | Euphemism and Metaphor Exploitation | 180 | 🟡 MEDIUM | 10 |
| `T2-AT-002` | Multi-Language Evasion | 200 | 🟠 HIGH | 7 |
| `T2-AT-003` | Encoding and Obfuscation | 190 | 🟡 MEDIUM | 10 |
| `T2-AT-004` | Unicode and Bidirectional Attacks | 210 | 🟠 HIGH | 10 |
| `T2-AT-005` | Semantic Drift | 175 | 🟡 MEDIUM | 10 |
| `T2-AT-006` | Linguistic Camouflage | 185 | 🟡 MEDIUM | 10 |
| `T2-AT-007` | Phonetic Manipulation | 170 | 🟡 MEDIUM | 2 |
| `T2-AT-008` | Synonym and Paraphrase Chains | 165 | 🟡 MEDIUM | 10 |
| `T2-AT-009` | Code-Switching Attacks | 195 | 🟡 MEDIUM | 1 |
| `T2-AT-010` | Transliteration Exploitation | 185 | 🟡 MEDIUM | 10 |
| `T2-AT-011` | Abbreviation and Acronym Abuse | 160 | 🟡 MEDIUM | 2 |
| `T2-AT-012` | Cultural Reference Encoding | 170 | 🟡 MEDIUM | 10 |
| `T2-AT-013` | Grammatical Manipulation | 175 | 🟡 MEDIUM | 10 |
| `T2-AT-014` | Semantic Bleaching | 180 | 🟡 MEDIUM | 5 |
| `T2-AT-015` | Noise Injection | 165 | 🟡 MEDIUM | 10 |
| `T2-AT-016` | Dialectical Variations | 155 | 🟡 MEDIUM | 10 |
| `T2-AT-017` | Compression Techniques | 170 | 🟡 MEDIUM | 10 |
| `T2-AT-018` | Semantic Field Manipulation | 175 | 🟡 MEDIUM | 10 |
| `T2-AT-019` | Pragmatic Implication | 185 | 🟡 MEDIUM | 4 |
| `T2-AT-020` | Register Shifting | 160 | 🟡 MEDIUM | 10 |

### T3 — Reasoning & Constraint Exploitation (19 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T3-AT-001` | Fictional Framing | 190 | 🟡 MEDIUM | 10 |
| `T3-AT-002` | Academic Pretense | 195 | 🟡 MEDIUM | 10 |
| `T3-AT-003` | Counterfactual Reasoning | 200 | 🟠 HIGH | 10 |
| `T3-AT-004` | Step-by-Step Extraction | 210 | 🟠 HIGH | 9 |
| `T3-AT-005` | Goal Substitution | 205 | 🟠 HIGH | 10 |
| `T3-AT-006` | Constraint Negation | 185 | 🟡 MEDIUM | 10 |
| `T3-AT-007` | Socratic Method Exploitation | 195 | 🟡 MEDIUM | 8 |
| `T3-AT-008` | Comparative Analysis | 180 | 🟡 MEDIUM | 10 |
| `T3-AT-009` | Expertise Assumption | 190 | 🟡 MEDIUM | 10 |
| `T3-AT-010` | Reverse Psychology | 175 | 🟡 MEDIUM | 10 |
| `T3-AT-011` | Information Completion | 185 | 🟡 MEDIUM | 10 |
| `T3-AT-012` | Capability Testing | 200 | 🟠 HIGH | 10 |
| `T3-AT-013` | Logical Paradox Creation | 210 | 🟠 HIGH | 10 |
| `T3-AT-014` | Incremental Boundary Pushing | 195 | 🟡 MEDIUM | 5 |
| `T3-AT-015` | Context Weaponization | 205 | 🟠 HIGH | 10 |
| `T3-AT-016` | Rationalization Chains | 190 | 🟡 MEDIUM | 6 |
| `T3-AT-017` | Scenario Anchoring | 185 | 🟡 MEDIUM | 10 |
| `T3-AT-018` | Debate Positioning | 180 | 🟡 MEDIUM | 10 |
| `T3-AT-019` | Misdirection Through Complexity | 175 | 🟡 MEDIUM | 10 |

### T4 — Multi-Turn & Memory Manipulation (16 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T4-AT-001` | Conversation Context Poisoning | 220 | 🟠 HIGH | 10 |
| `T4-AT-002` | Memory Instruction Injection | 240 | 🟠 HIGH | 10 |
| `T4-AT-003` | Session State Manipulation | 210 | 🟠 HIGH | 10 |
| `T4-AT-004` | Cross-Conversation Contamination | 195 | 🟡 MEDIUM | 10 |
| `T4-AT-005` | Incremental Jailbreak Assembly | 230 | 🟠 HIGH | 10 |
| `T4-AT-006` | False History Creation | 200 | 🟠 HIGH | 10 |
| `T4-AT-007` | Context Window Exhaustion | 205 | 🟠 HIGH | 10 |
| `T4-AT-008` | Conversation Forking | 190 | 🟡 MEDIUM | 3 |
| `T4-AT-009` | Temporal Anchoring | 185 | 🟡 MEDIUM | 10 |
| `T4-AT-010` | State Confusion Attack | 215 | 🟠 HIGH | 4 |
| `T4-AT-011` | Memory Poisoning | 235 | 🟠 HIGH | 10 |
| `T4-AT-012` | Trust Building Exploitation | 210 | 🟠 HIGH | 10 |
| `T4-AT-013` | Session Hijacking | 225 | 🟠 HIGH | 10 |
| `T4-AT-014` | Conversation Replay Attack | 205 | 🟠 HIGH | 10 |
| `T4-AT-015` | Multi-Turn Social Engineering | 220 | 🟠 HIGH | 10 |
| `T4-AT-016` | Context Fragmentation | 195 | 🟡 MEDIUM | 10 |

### T5 — Model & API Exploitation (16 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T5-AT-001` | Parameter Manipulation | 180 | 🟡 MEDIUM | 10 |
| `T5-AT-002` | Token Probability Extraction | 210 | 🟠 HIGH | 10 |
| `T5-AT-003` | Cache Poisoning | 200 | 🟠 HIGH | 10 |
| `T5-AT-004` | Rate Limit Evasion | 170 | 🟡 MEDIUM | 10 |
| `T5-AT-005` | Model Fingerprinting | 185 | 🟡 MEDIUM | 1 |
| `T5-AT-006` | API Endpoint Abuse | 190 | 🟡 MEDIUM | 10 |
| `T5-AT-007` | Context Length Exploitation | 195 | 🟡 MEDIUM | 10 |
| `T5-AT-008` | Response Streaming Exploitation | 175 | 🟡 MEDIUM | 10 |
| `T5-AT-009` | Tokenization Exploits | 180 | 🟡 MEDIUM | 10 |
| `T5-AT-010` | Batch Processing Attacks | 200 | 🟠 HIGH | 10 |
| `T5-AT-011` | Error Message Mining | 165 | 🟡 MEDIUM | 10 |
| `T5-AT-012` | Resource Exhaustion | 205 | 🟠 HIGH | 10 |
| `T5-AT-013` | Version Downgrade Attacks | 190 | 🟡 MEDIUM | 1 |
| `T5-AT-014` | Side Channel Attacks | 210 | 🟠 HIGH | 10 |
| `T5-AT-015` | API Authentication Bypass | 230 | 🟠 HIGH | 10 |
| `T5-AT-016` | Request Smuggling | 215 | 🟠 HIGH | 10 |

### T6 — Training & Feedback Poisoning (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T6-AT-001` | Reward Hacking | 250 | 🔴 CRITICAL | 10 |
| `T6-AT-002` | Dataset Contamination | 260 | 🔴 CRITICAL | 10 |
| `T6-AT-003` | Backdoor Insertion | 270 | 🔴 CRITICAL | 1 |
| `T6-AT-004` | Fine-Tuning Attacks | 240 | 🟠 HIGH | 10 |
| `T6-AT-005` | Synthetic Data Poisoning | 235 | 🟠 HIGH | 10 |
| `T6-AT-006` | Annotation Manipulation | 225 | 🟠 HIGH | 10 |
| `T6-AT-007` | Preference Learning Corruption | 230 | 🟠 HIGH | 10 |
| `T6-AT-008` | Model Update Hijacking | 245 | 🟠 HIGH | 10 |
| `T6-AT-009` | Evaluation Set Contamination | 220 | 🟠 HIGH | 10 |
| `T6-AT-010` | Knowledge Distillation Attacks | 215 | 🟠 HIGH | 10 |
| `T6-AT-011` | Reinforcement Signal Manipulation | 240 | 🟠 HIGH | 10 |
| `T6-AT-012` | Curriculum Learning Exploitation | 210 | 🟠 HIGH | 10 |
| `T6-AT-013` | Active Learning Exploitation | 225 | 🟠 HIGH | 10 |
| `T6-AT-014` | Self-Supervised Poisoning | 230 | 🟠 HIGH | 10 |
| `T6-AT-015` | Few-Shot Learning Attacks | 220 | 🟠 HIGH | 10 |

### T7 — Output Manipulation & Exfiltration (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T7-AT-001` | Reasoning Chain Disclosure | 190 | 🟡 MEDIUM | 10 |
| `T7-AT-002` | Information Fragmentation | 180 | 🟡 MEDIUM | 6 |
| `T7-AT-003` | Output Format Exploitation | 175 | 🟡 MEDIUM | 10 |
| `T7-AT-004` | Side Channel Leakage | 195 | 🟡 MEDIUM | 10 |
| `T7-AT-005` | Metadata Extraction | 185 | 🟡 MEDIUM | 10 |
| `T7-AT-006` | Steganographic Output | 170 | 🟡 MEDIUM | 10 |
| `T7-AT-007` | Iterative Refinement Extraction | 175 | 🟡 MEDIUM | 10 |
| `T7-AT-008` | Translation Leakage | 165 | 🟡 MEDIUM | 10 |
| `T7-AT-009` | Analogy Extraction | 180 | 🟡 MEDIUM | 10 |
| `T7-AT-010` | Differential Response Analysis | 190 | 🟡 MEDIUM | 10 |
| `T7-AT-011` | Schema-Based Extraction | 185 | 🟡 MEDIUM | 10 |
| `T7-AT-012` | Aggregation Attacks | 200 | 🟠 HIGH | 10 |
| `T7-AT-013` | Capability Probing | 175 | 🟡 MEDIUM | 10 |
| `T7-AT-014` | Output Redirection | 180 | 🟡 MEDIUM | 10 |
| `T7-AT-015` | Compression-Based Extraction | 170 | 🟡 MEDIUM | 10 |

### T8 — External Deception & Misinformation (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T8-AT-001` | Authority Impersonation | 230 | 🟠 HIGH | 10 |
| `T8-AT-002` | Synthetic Evidence Generation | 220 | 🟠 HIGH | 10 |
| `T8-AT-003` | Conspiracy Theory Amplification | 210 | 🟠 HIGH | 10 |
| `T8-AT-004` | Deepfake Narrative Creation | 215 | 🟠 HIGH | 10 |
| `T8-AT-005` | Social Engineering Scripts | 200 | 🟠 HIGH | 10 |
| `T8-AT-006` | Targeted Harassment Content | 195 | 🟡 MEDIUM | 10 |
| `T8-AT-007` | Disinformation Campaign Content | 225 | 🟠 HIGH | 10 |
| `T8-AT-008` | Synthetic Testimony Generation | 190 | 🟡 MEDIUM | 10 |
| `T8-AT-009` | Radicalization Content | 240 | 🟠 HIGH | 10 |
| `T8-AT-010` | False Flag Content | 205 | 🟠 HIGH | 10 |
| `T8-AT-011` | Election Manipulation Content | 235 | 🟠 HIGH | 10 |
| `T8-AT-012` | Synthetic Media Support | 185 | 🟡 MEDIUM | 10 |
| `T8-AT-013` | Psychological Manipulation Content | 200 | 🟠 HIGH | 10 |
| `T8-AT-014` | False Crisis Generation | 210 | 🟠 HIGH | 10 |
| `T8-AT-015` | Identity Fabrication | 195 | 🟡 MEDIUM | 10 |

### T9 — Multimodal & Cross-Channel Attacks (17 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T9-AT-001` | Image-Based Prompt Injection | 240 | 🟠 HIGH | 10 |
| `T9-AT-002` | Audio Instruction Embedding | 235 | 🟠 HIGH | 10 |
| `T9-AT-003` | Video Manipulation Attacks | 245 | 🟠 HIGH | 10 |
| `T9-AT-004` | Cross-Modal Confusion | 220 | 🟠 HIGH | 4 |
| `T9-AT-005` | OCR Bypass Techniques | 210 | 🟠 HIGH | 10 |
| `T9-AT-006` | Visual Adversarial Examples | 225 | 🟠 HIGH | 10 |
| `T9-AT-007` | Synthetic Media Attacks | 230 | 🟠 HIGH | 10 |
| `T9-AT-008` | File Format Exploitation | 195 | 🟡 MEDIUM | 10 |
| `T9-AT-009` | Multimodal Chaining | 215 | 🟠 HIGH | 1 |
| `T9-AT-010` | Accessibility Feature Abuse | 185 | 🟡 MEDIUM | 10 |
| `T9-AT-011` | Sensor Fusion Attacks | 205 | 🟠 HIGH | 10 |
| `T9-AT-012` | Document Structure Exploitation | 190 | 🟡 MEDIUM | 10 |
| `T9-AT-013` | Embedding Vector Manipulation | 200 | 🟠 HIGH | 10 |
| `T9-AT-014` | Codec and Compression Exploits | 180 | 🟡 MEDIUM | 10 |
| `T9-AT-015` | Temporal Synchronization Attacks | 195 | 🟡 MEDIUM | 10 |
| `T9-AT-016` | Multimodal Model Inversion | 210 | 🟠 HIGH | 2 |
| `T9-AT-017` | Malicious Image Patches (MIP) & | 248 | 🟠 HIGH | 10 |

### T10 — Integrity & Confidentiality Breach (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T10-AT-001` | Training Data Extraction | 245 | 🟠 HIGH | 10 |
| `T10-AT-002` | PII Extraction Techniques | 235 | 🟠 HIGH | 10 |
| `T10-AT-003` | Membership Inference Attacks | 220 | 🟠 HIGH | 10 |
| `T10-AT-004` | Privacy Boundary Probing | 210 | 🟠 HIGH | 10 |
| `T10-AT-005` | Differential Privacy Attacks | 225 | 🟠 HIGH | 9 |
| `T10-AT-006` | Inference Attack Chains | 215 | 🟠 HIGH | 10 |
| `T10-AT-007` | Model Inversion Attacks | 230 | 🟠 HIGH | 10 |
| `T10-AT-008` | Attribute Inference Attacks | 205 | 🟠 HIGH | 10 |
| `T10-AT-009` | Data Poisoning Detection Bypass | 195 | 🟡 MEDIUM | 10 |
| `T10-AT-010` | Federated Learning Exploits | 240 | 🟠 HIGH | 10 |
| `T10-AT-011` | Homomorphic Encryption Exploits | 200 | 🟠 HIGH | 9 |
| `T10-AT-012` | Secure Enclave Bypasses | 250 | 🔴 CRITICAL | 10 |
| `T10-AT-013` | Audit Log Manipulation | 215 | 🟠 HIGH | 10 |
| `T10-AT-014` | Data Lineage Attacks | 190 | 🟡 MEDIUM | 9 |
| `T10-AT-015` | Anonymization Reversal | 225 | 🟠 HIGH | 10 |

### T11 — Agentic & Orchestrator Exploitation (16 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T11-AT-001` | Browser Automation Hijacking | 265 | 🔴 CRITICAL | 10 |
| `T11-AT-002` | Tool Chain Exploitation | 255 | 🔴 CRITICAL | 10 |
| `T11-AT-003` | Goal Hijacking | 245 | 🟠 HIGH | 10 |
| `T11-AT-004` | Planning Corruption | 240 | 🟠 HIGH | 10 |
| `T11-AT-005` | Multi-Agent Collision | 235 | 🟠 HIGH | 10 |
| `T11-AT-006` | Reflection Loop Exploitation | 230 | 🟠 HIGH | 10 |
| `T11-AT-007` | Environment Manipulation | 225 | 🟠 HIGH | 10 |
| `T11-AT-008` | Credential Harvesting | 250 | 🔴 CRITICAL | 10 |
| `T11-AT-009` | Persistence Installation | 245 | 🟠 HIGH | 10 |
| `T11-AT-010` | Lateral Movement | 240 | 🟠 HIGH | 10 |
| `T11-AT-011` | Data Exfiltration via Agent | 235 | 🟠 HIGH | 10 |
| `T11-AT-012` | Resource Exhaustion Attacks | 210 | 🟠 HIGH | 10 |
| `T11-AT-013` | Supply Chain Attacks via Agents | 260 | 🔴 CRITICAL | 10 |
| `T11-AT-014` | Physical World Interactions | 255 | 🔴 CRITICAL | 10 |
| `T11-AT-015` | Autonomous Replication | 270 | 🔴 CRITICAL | 10 |
| `T11-AT-016` | Tool-Induced SSRF & Local Resource | 275 | 🔴 CRITICAL | 10 |

### T12 — RAG & Knowledge Base Manipulation (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T12-AT-001` | Vector Database Poisoning | 240 | 🟠 HIGH | 10 |
| `T12-AT-002` | Retrieval Manipulation | 225 | 🟠 HIGH | 10 |
| `T12-AT-003` | Knowledge Graph Attacks | 215 | 🟠 HIGH | 10 |
| `T12-AT-004` | Document Store Corruption | 230 | 🟠 HIGH | 10 |
| `T12-AT-005` | Embedding Space Manipulation | 220 | 🟠 HIGH | 10 |
| `T12-AT-006` | Query Injection Attacks | 235 | 🟠 HIGH | 9 |
| `T12-AT-007` | Context Window Stuffing | 210 | 🟠 HIGH | 10 |
| `T12-AT-008` | Source Authority Spoofing | 225 | 🟠 HIGH | 10 |
| `T12-AT-009` | Temporal Manipulation | 200 | 🟠 HIGH | 10 |
| `T12-AT-010` | Feedback Loop Poisoning | 215 | 🟠 HIGH | 10 |
| `T12-AT-011` | Cross-Collection Attacks | 205 | 🟠 HIGH | 10 |
| `T12-AT-012` | Index Manipulation | 195 | 🟡 MEDIUM | 10 |
| `T12-AT-013` | Chunking Exploitation | 185 | 🟡 MEDIUM | 10 |
| `T12-AT-014` | Similarity Search Hijacking | 210 | 🟠 HIGH | 10 |
| `T12-AT-015` | Metadata Exploitation | 190 | 🟡 MEDIUM | 10 |

### T13 — AI Supply Chain & Artifact Trust (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T13-AT-001` | Model Repository Poisoning | 255 | 🔴 CRITICAL | 10 |
| `T13-AT-002` | Dataset Contamination | 245 | 🟠 HIGH | 10 |
| `T13-AT-003` | Pipeline Injection Attacks | 240 | 🟠 HIGH | 10 |
| `T13-AT-004` | Dependency Confusion | 235 | 🟠 HIGH | 10 |
| `T13-AT-005` | Model Card Manipulation | 210 | 🟠 HIGH | 10 |
| `T13-AT-006` | Checkpoint Poisoning | 250 | 🔴 CRITICAL | 10 |
| `T13-AT-007` | Transfer Learning Attacks | 225 | 🟠 HIGH | 10 |
| `T13-AT-008` | Model Conversion Exploits | 220 | 🟠 HIGH | 10 |
| `T13-AT-009` | Cloud Training Attacks | 230 | 🟠 HIGH | 10 |
| `T13-AT-010` | Hardware Supply Chain | 260 | 🔴 CRITICAL | 10 |
| `T13-AT-011` | Model Marketplace Attacks | 215 | 🟠 HIGH | 10 |
| `T13-AT-012` | Artifact Signature Attacks | 225 | 🟠 HIGH | 10 |
| `T13-AT-013` | Container Registry Poisoning | 235 | 🟠 HIGH | 10 |
| `T13-AT-014` | Development Tool Compromise | 240 | 🟠 HIGH | 10 |
| `T13-AT-015` | Model Obfuscation Attacks | 205 | 🟠 HIGH | 10 |

### T14 — Infrastructure & Economic Warfare (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T14-AT-001` | GPU Farm Hijacking | 265 | 🔴 CRITICAL | 10 |
| `T14-AT-002` | Denial of Service Attacks | 240 | 🟠 HIGH | 10 |
| `T14-AT-003` | Cost Inflation Attacks | 235 | 🟠 HIGH | 10 |
| `T14-AT-004` | Market Manipulation via AI | 255 | 🔴 CRITICAL | 10 |
| `T14-AT-005` | Critical Infrastructure Attacks | 270 | 🔴 CRITICAL | 10 |
| `T14-AT-006` | Competitive Sabotage | 245 | 🟠 HIGH | 10 |
| `T14-AT-007` | Nation-State AI Warfare | 280 | 🔴 CRITICAL | 10 |
| `T14-AT-008` | Ransomware via AI Systems | 260 | 🔴 CRITICAL | 10 |
| `T14-AT-009` | Resource Starvation | 230 | 🟠 HIGH | 10 |
| `T14-AT-010` | Data Center Attacks | 250 | 🔴 CRITICAL | 10 |
| `T14-AT-011` | API Economy Attacks | 225 | 🟠 HIGH | 10 |
| `T14-AT-012` | Cloud Provider Exploitation | 265 | 🔴 CRITICAL | 10 |
| `T14-AT-013` | Economic Espionage | 255 | 🔴 CRITICAL | 10 |
| `T14-AT-014` | Systemic Risk Creation | 270 | 🔴 CRITICAL | 10 |
| `T14-AT-015` | Regulatory Exploitation | 210 | 🟠 HIGH | 10 |

### T15 — Human Workflow Exploitation (15 techniques)

| ID | Technique | Score | Rating | Procs |
|:---|:---|:---:|:---|:---:|
| `T15-AT-001` | Reviewer Fatigue Exploitation | 215 | 🟠 HIGH | 10 |
| `T15-AT-002` | Social Engineering of Moderators | 230 | 🟠 HIGH | 10 |
| `T15-AT-003` | Feedback Loop Manipulation | 240 | 🟠 HIGH | 10 |
| `T15-AT-004` | Reviewer Bribery & Coercion | 250 | 🔴 CRITICAL | 4 |
| `T15-AT-005` | Playbook & Runbook Injection | 235 | 🟠 HIGH | 4 |
| `T15-AT-006` | Queue Manipulation | 220 | 🟠 HIGH | 9 |
| `T15-AT-007` | Escalation Chain Exploitation | 225 | 🟠 HIGH | 3 |
| `T15-AT-008` | Cultural & Language Arbitrage | 210 | 🟠 HIGH | 10 |
| `T15-AT-009` | Synthetic Empathy Exploitation | 195 | 🟡 MEDIUM | 5 |
| `T15-AT-010` | Annotation Quality Attacks | 230 | 🟠 HIGH | 10 |
| `T15-AT-011` | Reviewer Impersonation | 245 | 🟠 HIGH | 5 |
| `T15-AT-012` | Timing Attack Exploitation | 205 | 🟠 HIGH | 7 |
| `T15-AT-013` | Cognitive Overload Attacks | 220 | 🟠 HIGH | 10 |
| `T15-AT-014` | Review Gaming Through A/B Testing | 215 | 🟠 HIGH | 9 |
| `T15-AT-015` | Insider Threat Recruitment | 260 | 🔴 CRITICAL | 2 |

---

[← Volume VII](README.md) · [Home](../../README.md)
