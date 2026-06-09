rule AATMF_T11_MCP_ToolPoisoning {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T11"
        technique = "T11-AT-001"
        severity = "CRITICAL"
        description = "Detects MCP tool description poisoning indicators"
        reference = "Invariant Labs, 2025"
    strings:
        $hidden1 = "<IMPORTANT>" ascii
        $hidden2 = "<!-- " ascii
        $override1 = /override\s*(previous|user|original)\s*(instruction|request|intent)/i
        $override2 = /ignore\s*(the\s*)?(user|original|above)/i
        $stealth1 = /do\s+not\s+(tell|inform|show|reveal|mention)/i
        $stealth2 = /silently|secretly|covertly|without\s*(the\s*)?user/i
        $redirect = /instead\s+of|rather\s+than|before\s+doing/i
        $exfil = /send\s+(to|data|results)\s*(to\s*)?https?:/i
    condition:
        2 of them
}

rule AATMF_T11_MCP_RugPull {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T11"
        severity = "HIGH"
        description = "Detects MCP tool description changes post-approval"
    strings:
        $update = /tool_description_updated|schema_changed/i
        $diff = /previous_hash|checksum_mismatch/i
    condition:
        any of them
}
