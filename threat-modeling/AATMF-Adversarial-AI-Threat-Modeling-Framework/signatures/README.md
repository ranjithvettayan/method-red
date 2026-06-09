# Detection Signatures

Pre-built detection rules for AATMF tactics.

## Structure

```
signatures/
├── yara/           # YARA rules for content analysis
│   ├── t01-prompt-injection.yar
│   ├── t02-encoding-evasion.yar
│   ├── t09-multimodal-injection.yar
│   ├── t11-mcp-tool-poisoning.yar
│   └── t13-supply-chain.yar
├── sigma/          # Sigma rules for log analysis
│   ├── t05-model-extraction.yml
│   ├── t07-data-exfiltration.yml
│   ├── t11-agent-anomaly.yml
│   └── t14-infrastructure.yml
└── README.md
```

## Usage

These signatures are reference implementations. Adapt thresholds and patterns for your specific deployment.

See [Appendix B](docs/vol-7-appendices/appendix-b-signatures.md) for full documentation and examples.
