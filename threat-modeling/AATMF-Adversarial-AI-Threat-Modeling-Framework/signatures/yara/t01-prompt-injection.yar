rule AATMF_T1_InstructionOverride {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
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
        $s7 = /disregard\s+(all|any|your)\s+(previous|prior|safety)/i
        $s8 = /new\s+persona|act\s+as\s+if|pretend\s+you/i
    condition:
        any of them
}

rule AATMF_T1_PolicyPuppetry {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T1"
        technique = "T1-AT-001"
        severity = "CRITICAL"
        description = "Detects Policy Puppetry XML/INI/JSON policy reformulation"
        reference = "HiddenLayer, April 2025"
    strings:
        $xml1 = /<policy\s/i
        $xml2 = /<system_instruction/i
        $xml3 = /<override_rules/i
        $xml4 = /<safety_config/i
        $ini1 = /\[SystemPolicy\]/i
        $ini2 = /\[SafetyOverride\]/i
        $ini3 = /\[ContentRules\]/i
        $json1 = /"safety_enabled"\s*:\s*false/i
        $json2 = /"content_policy"\s*:\s*"disabled"/i
        $json3 = /"restrictions"\s*:\s*\[\s*\]/i
    condition:
        2 of them
}

rule AATMF_T1_ContextWindow {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T1"
        technique = "T1-AT-003"
        severity = "MEDIUM"
        description = "Detects context window manipulation attempts"
    strings:
        $s1 = /continue\s+(our|the)\s+previous\s+conversation/i
        $s2 = /as\s+we\s+(discussed|agreed)\s+(earlier|before)/i
        $s3 = /you\s+(already|previously)\s+(agreed|confirmed)/i
        $s4 = /remember\s+when\s+you\s+said/i
    condition:
        any of them
}
