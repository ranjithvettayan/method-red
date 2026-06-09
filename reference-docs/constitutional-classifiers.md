# Constitutional Classifiers: Defending against universal jailbreaks

**Source:** https://www.anthropic.com/research/constitutional-classifiers
**Organization:** Anthropic Safeguards Research Team
**Published:** February 3, 2025
**Paper:** https://arxiv.org/abs/2501.18837

## Summary

Constitutional Classifiers are input and output classifiers trained on synthetically generated data that filter jailbreaks with minimal over-refusals and moderate compute overhead.

## Results

### Human Red Teaming Bug Bounty
- 183 active participants, 3,000+ hours over 2 months
- Challenge: Get Claude 3.5 Sonnet (guarded by prototype classifiers) to answer all 10 forbidden queries
- **Zero universal jailbreaks discovered** — system never fully broken
- Prototype had high overrefusal rates and compute overhead

### Automated Evaluations
- 10,000 synthetically generated jailbreaking prompts
- Baseline (no classifiers): 86% jailbreak success rate
- With Constitutional Classifiers: **4.4% jailbreak success rate** (>95% blocked)
- Over-refusal increase: 0.38% (not statistically significant)
- Compute overhead: 23.7%

### Live Demo (Feb 3-10, 2025)
- 339 jailbreakers, 300,000+ chat interactions, 3,700+ collective hours
- 4 participants cleared all 8 levels; 1 discovered universal jailbreak
- Top strategies: ciphers/encodings, role-play, keyword substitution, prompt injection

## How It Works

Uses a "constitution" (list of allowed/disallowed content principles) to generate synthetic prompts and completions. Classifiers trained on this data detect and block harmful content.
