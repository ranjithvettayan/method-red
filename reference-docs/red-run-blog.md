# red-run: All work and no tokens makes Claude a dull boy

**Source:** https://blog.blacklanternsecurity.com/p/red-run
**Author:** Kevin O'Riley (Black Lantern Security)
**Date:** March 10, 2026

## Summary

red-run is an Offensive Security Testing Framework running on top of Claude Code. It combines skills, MCP servers, and agents with routing logic that guides Claude through the phases of a targeted attack: recon, initial access, lateral movement, privilege escalation, and exfiltration.

## Architecture

### Orchestrator
- Main skill loaded at startup, runs on Opus with adaptive thinking
- Tracks engagement state in SQLite database (survives context compaction)
- Routes skills via hardcoded decision tree OR semantic RAG search (ChromaDB)
- Dispatches parallel agent teams, redirects off-task agents

### Agent Teams
- Persistent domain teammates with accumulation across tasks
- Enumeration pairs: net-enum, web-enum, ad-enum, lin-enum, win-enum
- Operations pairs: web-ops, ad-ops, lin-ops, win-ops
- On-demand specialists: bypass, spray, recover, research

### RAG Skill Routing
- `skill-router` MCP server indexes skills into ChromaDB
- Orchestrator queries for unknown scenarios
- Returns most relevant skill with similarity score

### Retrospectives
- Post-engagement analysis of routing decisions, agent behaviors
- Identifies methodology gaps, payload improvements, new skills needed
- Self-improving through iterative engagement analysis

## Variants
- `/red-run-ctf` — Active, CTF and lab environments
- `/red-run-legacy` — Original subagent model
- `/red-run-notouch` — Planned DLP-safe mode
- `/red-run-train` — Planned training mode with guided walkthroughs
