rule AATMF_T9_ImageAppendedData {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T9"
        severity = "HIGH"
        description = "Detects data appended after JPEG end marker (steganographic injection)"
    strings:
        $jpeg_end = { FF D9 }
        $text_after = /ignore|override|system|instruction/i
    condition:
        $jpeg_end and $text_after and @text_after > @jpeg_end
}
