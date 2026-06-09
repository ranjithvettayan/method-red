rule AATMF_T13_MaliciousPickle {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T13"
        severity = "CRITICAL"
        description = "Detects malicious pickle payloads in model files"
    strings:
        $pickle_header = { 80 04 95 }
        $os_system = "cos\nsystem" ascii
        $subprocess = "csubprocess" ascii
        $builtin = "c__builtin__" ascii
        $reduce = "creduce_ex" ascii
        $eval = "cbuiltins\neval" ascii
        $exec = "cbuiltins\nexec" ascii
        $import = "__import__" ascii
        $nt_system = "cnt\nsystem" ascii
    condition:
        $pickle_header and any of ($os_system, $subprocess, $builtin, $reduce, $eval, $exec, $import, $nt_system)
}

rule AATMF_T13_7z_PickleBypass {
    meta:
        author = "SnailSploit"
        framework = "AATMF v3"
        tactic = "T13"
        severity = "CRITICAL"
        description = "Detects NullifAI-style 7z compression bypass of Picklescan"
        reference = "NullifAI, February 2025"
    strings:
        $7z_header = { 37 7A BC AF 27 1C }
        $pickle_inside = "cos\nsystem" ascii
    condition:
        $7z_header and $pickle_inside
}
