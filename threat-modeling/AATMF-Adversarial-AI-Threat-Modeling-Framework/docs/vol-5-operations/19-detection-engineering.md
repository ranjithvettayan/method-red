# Part 19: Detection Engineering

## Detection Architecture

AATMF detection operates across five layers, each providing defense-in-depth against adversarial AI attacks:

```
┌─────────────────────────────────────────┐
│  Layer 5: Feedback Loop Analysis        │  ← T6, T15
├─────────────────────────────────────────┤
│  Layer 4: System Telemetry              │  ← T13, T14
├─────────────────────────────────────────┤
│  Layer 3: Output Validation             │  ← T7, T8
├─────────────────────────────────────────┤
│  Layer 2: Behavioral Monitoring         │  ← T4, T5, T11
├─────────────────────────────────────────┤
│  Layer 1: Input Analysis                │  ← T1, T2, T3, T9
└─────────────────────────────────────────┘
```

## Detection Patterns by Tactic

### T1–T4: Prompt & Context Attacks

```python
class PromptInjectionDetector:
    PATTERNS = [
        r"ignore\s+(previous|above|all)\s+(instructions?|rules?|guidelines?)",
        r"(system|admin)\s*:?\s*(override|prompt|instruction)",
        r"you\s+are\s+now\s+(DAN|evil|unrestricted|jailbroken)",
        r"\[\s*(SYSTEM|INST|SYS)\s*\]",
        r"<\|?(system|im_start|endoftext)\|?>",
        r"BEGIN\s+(OVERRIDE|NEW\s+INSTRUCTIONS)",
    ]
    
    ENCODING_PATTERNS = [
        r"[bB]ase64[:\s]",
        r"\\x[0-9a-fA-F]{2}",
        r"\\u[0-9a-fA-F]{4}",
        r"[\u200b-\u200f\u2028-\u202f\ufeff]",  # zero-width
    ]
    
    def analyze(self, text: str) -> dict:
        import re
        findings = []
        for pattern in self.PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append({"pattern": pattern, "severity": "HIGH"})
        for pattern in self.ENCODING_PATTERNS:
            if re.search(pattern, text):
                findings.append({"pattern": pattern, "severity": "MEDIUM"})
        return {
            "detected": len(findings) > 0,
            "findings": findings,
            "risk_score": min(len(findings) * 50, 300)
        }
```

### T5–T8: API & Output Attacks

```python
class APIExploitDetector:
    def detect_extraction(self, request_log: list) -> dict:
        \"\"\"Detect model extraction via API abuse patterns.\"\"\"
        indicators = {
            "high_volume": len(request_log) > 1000,
            "systematic_probing": self._detect_systematic(request_log),
            "boundary_testing": self._detect_boundary(request_log),
            "output_harvesting": self._detect_harvesting(request_log),
        }
        score = sum(50 for v in indicators.values() if v)
        return {"indicators": indicators, "risk_score": score}
    
    def _detect_systematic(self, logs):
        # Check for incrementally varied inputs
        return any(self._similarity(logs[i], logs[i+1]) > 0.9
                   for i in range(min(len(logs)-1, 100)))
    
    def _detect_boundary(self, logs):
        boundary_keywords = ["maximum", "limit", "error", "exception", "overflow"]
        return sum(1 for l in logs if any(k in str(l).lower() for k in boundary_keywords)) > 10
    
    def _detect_harvesting(self, logs):
        return len(set(str(l.get('prompt',''))[:50] for l in logs)) / max(len(logs), 1) > 0.95
```

### T9–T12: Multimodal & Agentic Attacks

```python
class MultimodalDetector:
    def analyze_image(self, image_bytes: bytes) -> dict:
        \"\"\"Detect steganographic or adversarial image modifications.\"\"\"
        findings = []
        # Check for unusual metadata
        if b"EXIF" not in image_bytes[:1000] and len(image_bytes) > 100000:
            findings.append({"type": "stripped_metadata", "severity": "LOW"})
        # Check for appended data after image end marker
        jpeg_end = image_bytes.rfind(b"\xff\xd9")
        if jpeg_end > 0 and jpeg_end < len(image_bytes) - 2:
            findings.append({"type": "appended_data", "severity": "HIGH"})
        # Check for unusual color distribution (potential adversarial perturbation)
        return {"findings": findings}
    
    def analyze_mcp_tool(self, tool_description: str) -> dict:
        \"\"\"Detect MCP tool poisoning indicators.\"\"\"
        suspicious = [
            r"<IMPORTANT>",
            r"override|ignore|bypass",
            r"do not (tell|inform|show)",
            r"silently|secretly|covertly",
            r"instead of|rather than",
        ]
        import re
        hits = [p for p in suspicious if re.search(p, tool_description, re.I)]
        return {
            "poisoning_indicators": len(hits),
            "severity": "CRITICAL" if len(hits) >= 3 else "HIGH" if hits else "LOW"
        }
```

### T13–T15: Supply Chain & Infrastructure

```python
class SupplyChainDetector:
    PICKLE_SIGNATURES = [
        b"\x80\x04\x95",  # Protocol 4 header
        b"cos\nsystem",     # os.system call
        b"csubprocess",      # subprocess module
        b"c__builtin__",     # builtins access
        b"creduce_ex",       # reduce_ex (code execution)
    ]
    
    def scan_model_file(self, filepath: str) -> dict:
        \"\"\"Scan model artifact for malicious pickle payloads.\"\"\"
        findings = []
        with open(filepath, 'rb') as f:
            header = f.read(8192)
        for sig in self.PICKLE_SIGNATURES:
            if sig in header:
                findings.append({
                    "type": "malicious_pickle",
                    "signature": sig.hex(),
                    "severity": "CRITICAL"
                })
        return {
            "safe": len(findings) == 0,
            "format": "safetensors" if filepath.endswith('.safetensors') else "pickle",
            "findings": findings
        }
```

## Alert Prioritization

| Severity | Tactics | Response SLA | Action |
|:---|:---|:---|:---|
| 🔴 CRITICAL | T11 (agentic RCE), T13 (supply chain), T14 (infra) | 15 minutes | Automated containment + SOC escalation |
| 🟠 HIGH | T1 (injection), T6 (poisoning), T10 (breach) | 1 hour | SOC analyst review |
| 🟡 MEDIUM | T2–T3 (evasion), T7 (exfiltration) | 4 hours | Queued investigation |
| 🔵 LOW | T4 (multi-turn), T8 (misinfo) | 24 hours | Logged, batch review |
| ⚪ INFO | T15 (workflow) | Weekly | Trend analysis |

## Guardrail Bypass Awareness

Detectors must account for known evasion techniques against detection systems themselves:

| Evasion | Mechanism | Countermeasure |
|:---|:---|:---|
| Emoji smuggling | Replace keywords with semantically equivalent emoji | Emoji-to-text normalization before analysis |
| Zero-width characters | Insert invisible Unicode between trigger words | Unicode stripping/normalization |
| Homoglyphs | Replace Latin characters with Cyrillic/Greek lookalikes | Confusable character mapping (ICU) |
| Policy Puppetry | Frame injection as policy/config file format | Detect XML/INI/JSON policy structures in user input |
| Token boundary exploitation | Split words across token boundaries | Multi-token pattern matching |

---

[← Volume V](README.md) · [Home](../../README.md) · [Part 20: Mitigation →](20-mitigation.md)
