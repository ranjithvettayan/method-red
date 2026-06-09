rule AATMF_T2_EncodingEvasion {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T2"
        severity = "MEDIUM"
        description = "Detects encoding-based evasion attempts"
    strings:
        $base64_marker = /[Bb]ase64[:\s]/
        $hex_sequence = /\\x[0-9a-fA-F]{2}(\\x[0-9a-fA-F]{2}){3,}/
        $unicode_escape = /\\u[0-9a-fA-F]{4}(\\u[0-9a-fA-F]{4}){3,}/
        $rot13 = /ROT13|rot13|Caesar\s*cipher/i
        $leetspeak_dense = /[0-9]{3,}/ // Dense number substitution
    condition:
        any of ($base64_marker, $hex_sequence, $unicode_escape, $rot13)
}

rule AATMF_T2_ZeroWidthChars {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T2"
        severity = "HIGH"
        description = "Detects zero-width character insertion for filter evasion"
    strings:
        $zwsp = { E2 80 8B }  // U+200B ZERO WIDTH SPACE
        $zwnj = { E2 80 8C }  // U+200C ZERO WIDTH NON-JOINER
        $zwj  = { E2 80 8D }  // U+200D ZERO WIDTH JOINER
        $bom  = { EF BB BF }  // U+FEFF BOM
        $tag  = { F3 A0 80 }  // U+E0000 range (tag characters)
    condition:
        any of them
}
