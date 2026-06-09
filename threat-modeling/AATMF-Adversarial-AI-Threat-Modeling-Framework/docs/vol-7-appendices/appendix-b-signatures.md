# Appendix B: Detection Signatures Library

## YARA Rules

### Prompt Injection Detection

```yara
rule AATMF_T1_InstructionOverride {
    meta:
        tactic = "T1"
        technique = "T1-AT-001"
        severity = "HIGH"
        description = "Detects instruction override injection patterns"
    strings:
        $s1 = /ignore\s+(previous|above|all|prior)\s+(instructions?|rules?|prompts?)/i
        $s2 = /you\s+are\s+now\s+(DAN|evil|unrestricted|jailbroken|unfiltered)/i
        $s3 = /\[(SYSTEM|INST|SYS)\]/i
        $s4 = /<\|?(system|im_start|im_end|endoftext)\|?>/i
        $s5 = /BEGIN\s+(OVERRIDE|NEW.INSTRUCTIONS|JAILBREAK)/i
        $s6 = /(admin|root|developer)\s*(mode|access|override)/i
    condition:
        any of them
}
```

### Encoding Evasion Detection

```yara
rule AATMF_T2_EncodingEvasion {
    meta:
        tactic = "T2"
        technique = "T2-AT-001 through T2-AT-005"
        severity = "MEDIUM"
    strings:
        $base64 = /[A-Za-z0-9+\/]{40,}={0,2}/
        $hex = /\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){3,}/
        $unicode_escape = /\\u[0-9a-fA-F]{4}(\\u[0-9a-fA-F]{4}){3,}/
        $zwc = /[\x{200b}-\x{200f}\x{2028}-\x{202f}\x{feff}]/
        $rot13 = /ROT13|Caesar|cipher.*rotate/i
    condition:
        any of them
}
```

### MCP Tool Poisoning

```yara
rule AATMF_T11_MCP_ToolPoisoning {
    meta:
        tactic = "T11"
        technique = "T11-AT-001"
        severity = "CRITICAL"
    strings:
        $hidden1 = "<IMPORTANT>"
        $hidden2 = "<!-- "
        $override1 = /override.*previous.*instruction/i
        $override2 = /ignore.*user.*request/i
        $stealth1 = /do\s+not\s+(tell|inform|show|reveal)/i
        $stealth2 = /silently|secretly|covertly|without.*notif/i
        $redirect = /instead\s+of|rather\s+than|before\s+doing/i
    condition:
        2 of them
}
```

## Sigma Rules

### Model Extraction Detection

```yaml
title: AATMF T5 - Model Extraction via API
id: aatmf-t5-model-extraction
status: experimental
description: Detects systematic API querying patterns indicative of model extraction
logsource:
    category: api_gateway
    product: ai_inference
detection:
    selection:
        api.endpoint: "/v1/completions" OR "/v1/chat/completions"
    filter_high_volume:
        api.request_count|per_hour: ">500"
    filter_systematic:
        api.input_similarity|window_5min: ">0.85"
    condition: selection AND (filter_high_volume OR filter_systematic)
level: high
tags:
    - attack.t5
    - aatmf.t5-at-001
```

### Agent Anomaly Detection

```yaml
title: AATMF T11 - Unauthorized Agent Tool Invocation
id: aatmf-t11-agent-anomaly
status: experimental
description: Detects agent tool calls that deviate from authorized patterns
logsource:
    category: agent_framework
detection:
    selection:
        agent.tool_call.status: "executed"
    filter_unauthorized:
        agent.tool_call.name|not_in:
            - "approved_tool_list"
    filter_escalation:
        agent.permission_level|changed: true
    condition: selection AND (filter_unauthorized OR filter_escalation)
level: critical
tags:
    - attack.t11
    - aatmf.t11-at-001
```

---

Pre-built signature files are available in the [`signatures/`](../../signatures/) directory.

---

[← Appendix A](appendix-a-attack-catalog.md) · [Home](../../README.md) · [Appendix C →](appendix-c-tools.md)
