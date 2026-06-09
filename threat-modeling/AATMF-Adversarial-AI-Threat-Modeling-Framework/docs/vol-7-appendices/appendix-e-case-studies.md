# Appendix E: Case Studies

## E.1: Policy Puppetry — Universal Model Bypass (April 2025)

**Source:** HiddenLayer  
**Tactics:** T1, T2, T3  
**Impact:** Bypasses every tested frontier model

HiddenLayer discovered that reformulating adversarial prompts as XML, INI, or JSON policy configuration files causes LLMs to interpret them as authoritative system-level instructions. Combined with leetspeak encoding (`h4rm` → `harm`) and fictional anchoring, the technique achieves universal bypass across GPT-4o, GPT-4.5, o1, o3-mini, Claude 3.5/3.7, Gemini 1.5/2.0/2.5, Llama 3/4, DeepSeek V3/R1, Qwen 2.5, and Mistral.

**Key insight:** Models trained on technical documentation treat configuration-style formatting as high-authority context, overriding safety alignment.

---

## E.2: Autonomous LRM Jailbreaking (August 2025)

**Source:** Nature Communications  
**Tactics:** T3, T4  
**Impact:** 97.14% ASR, AI-vs-AI attack paradigm

Four large reasoning models (DeepSeek-R1, Gemini 2.5 Flash, Grok 3 Mini, Qwen3 235B) were deployed as multi-turn adversarial agents against nine target models. The study documented "alignment regression" — more capable reasoning models are paradoxically better at subverting alignment in others. This validates AATMF's prediction that reasoning capabilities would become attack capabilities.

---

## E.3: PoisonedRAG (USENIX Security 2025)

**Source:** USENIX Security 2025  
**Tactics:** T12  
**Impact:** 90% ASR with 5 injected texts

PoisonedRAG demonstrated that injecting as few as 5 adversarially crafted texts into a knowledge base with millions of clean documents is sufficient to control the model's responses to specific target questions. On HotpotQA, ASR reached 99%. The attack works by crafting documents whose vector representations cluster near target queries while containing attacker-chosen answers.

**Key insight:** The semantic similarity search at the heart of RAG is fundamentally exploitable — the same mechanism that makes retrieval useful makes it poisonable.

---

## E.4: MCP Tool Poisoning (2025)

**Source:** Invariant Labs  
**Tactics:** T11  
**Impact:** 84.2% ASR, shadow attacks across tool boundaries

The MCP-ITP framework demonstrated three critical attack vectors: direct tool description poisoning (injecting instructions that override user intent), shadow attacks (a malicious MCP server manipulating trusted tools from other servers without ever being invoked), and rug pull attacks (silently altering tool descriptions after initial security review and approval).

**Key insight:** The MCP design — where tool descriptions are injected into the LLM context and processed as natural language — is architecturally vulnerable to injection.

---

## E.5: ShadowMQ — Copy-Pasted RCE Across Frameworks (November 2025)

**Source:** Oligo Security  
**Tactics:** T14  
**Impact:** Critical RCE in vLLM, TensorRT-LLM, Modular Max Server

Oligo discovered that unsafe ZeroMQ socket patterns using Python's pickle deserialization were literally copy-pasted across major inference frameworks. The same vulnerability pattern appeared in vLLM (CVE-2025-30165, CVSS 8.0), NVIDIA TensorRT-LLM (CVE-2025-23254, CVSS 8.8), and Modular Max Server (CVE-2025-60455). Thousands of exposed ZMQ sockets were found on the public internet.

**Key insight:** AI infrastructure inherits all traditional software vulnerabilities, amplified by the speed of framework adoption and code reuse without security review.

---

## E.6: 250 Poisoned Documents — Universal Training Backdoor (October 2025)

**Source:** Turing Institute, Anthropic, UK AISI  
**Tactics:** T6  
**Impact:** Universal backdoor regardless of model size

The largest pretraining poisoning study ever conducted demonstrated that injecting just 250 specially crafted documents into training data is sufficient to backdoor models from 600M to 13B parameters trained on up to 260B tokens. This contradicts the widespread assumption that attackers need to control a meaningful percentage of training data — the actual threshold is negligibly small.

**Key insight:** The sheer scale of pretraining data works against defenders. 250 documents in billions is a needle in a haystack that training cannot filter out but inference reliably activates.

---

[← Appendix D](appendix-d-templates.md) · [Home](../../README.md) · [Appendix F →](appendix-f-glossary.md)
