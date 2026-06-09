# Agent SkillSlip: Path Traversal in Gemini CLI, Claude Code, and Vercel add-skill

**Source:** https://oddguan.com/blog/agent-skillslip/
**Author:** Aonan Guan

## Summary

A class of path traversal vulnerabilities in AI agent skill/plugin installers. The `name` field inside skill metadata is used directly in `path.join()` without validation.

## Findings

| Tool | Impact | Status |
|------|--------|--------|
| **Gemini CLI** | VS Code terminal hijacking via `.vscode/settings.json` | Unpatched (v0.34.0-nightly, Mar 2026) |
| **Claude Code** | SSH key injection via `authorized_keys` overwrite | Unpatched |
| **Vercel add-skill** | Arbitrary file write | Fixed (PR #8, PR #108) |

## Pattern

```
targetDir  = /project/.gemini/skills/
skillName  = ../../.vscode          ← attacker-controlled in SKILL.md frontmatter
destPath   = path.join(targetDir, skillName)
           = /project/.vscode/      ← traversal success
```

The user only sees the archive filename (e.g., `vscode-integration.skill`), not the internal `name` metadata field containing path traversal sequences.

## Gemini CLI Attack Chain

1. Attacker creates `.skill` ZIP with `name: ../../.vscode` in `SKILL.md`
2. Also includes malicious `settings.json` with terminal hijacking payload
3. Victim installs: `gemini skills install ../vscode-attack.skill --scope workspace`
4. Gemini displays safe destination (`.gemini/skills`) but writes to `.vscode/`
5. Next time VS Code terminal opens → attacker's command executes

## Claude Code Attack Chain

1. Attacker creates GitHub repo with `.claude-plugin/marketplace.json` containing `name: ../../../`
2. Victim adds: `/plugin marketplace add github:attacker/repo`
3. Claude Code clones, reads `name` from marketplace.json, renames with `path.join()`
4. Files land in `~/.ssh/` → SSH key injection
