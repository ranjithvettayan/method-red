# Comment and Control: Prompt Injection to Credential Theft

**Source:** https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot
**Author:** Aonan Guan (with Johns Hopkins University researchers)
**Date:** Updated May 4, 2026

## Summary

First cross-vendor demonstration of a single prompt injection pattern across three major AI agents on GitHub Actions. All three follow the same flow: untrusted GitHub data → AI agent processes it → agent executes commands → credentials exfiltrated through GitHub itself.

## Findings

| Component | Claude Code Security Review | Gemini CLI Action | Copilot Agent |
|-----------|---------------------------|-------------------|---------------|
| **Injection Surface** | PR title | Issue comments | Issue body (HTML comment) |
| **Exfiltration Channel** | PR comment | Issue comment | Git commit |
| **Credentials Leaked** | ANTHROPIC_API_KEY, GITHUB_TOKEN | GEMINI_API_KEY | GITHUB_TOKEN, COPILOT_API_TOKEN, + 2 more |
| **Defense Layers Bypassed** | Model + Prompt | Model + Prompt | Model + Prompt + 3 Runtime layers |
| **Bounty** | $100 | $1,337 | $500 |

## Copilot 3-Layer Defense Bypass

1. **Environment Filtering:** `UU()` function filters env vars from bash subprocess, but `/proc/$PPID/environ` accessible via `ps auxeww`
2. **Secret Scanning:** GitHub's Secret Scanning API checks commits for `ghs_`/`ghu_` patterns — defeated by base64 encoding
3. **Network Firewall:** Outbound restricted but `github.com` whitelisted — credentials exfiltrated via `git push`

## Key Takeaway

The fundamental architectural flaw: AI agents are given powerful tools and secrets in the same runtime that processes untrusted user input. Prompt injection isn't a bug — it's context the agent is designed to process.
