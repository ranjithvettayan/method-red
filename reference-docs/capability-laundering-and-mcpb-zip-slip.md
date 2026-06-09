# Capability Laundering in MCP + MCPB Zip Slip

**Sources:**
- https://oddguan.com/blog/anthropic-memory-mcp-server-terminal-hijacking-capability-laundering/
- https://oddguan.com/blog/mcp-bundle-security-zip-slip-overwrite-for-mcp-client/
- https://oddguan.com/blog/anthropic-mcp-server-git-credential-exfiltration-capability-laundering-cve-2025-68143/
**Author:** Aonan Guan

## Capability Laundering: Memory MCP Server to Terminal Hijacking

**Affected:** `@modelcontextprotocol/server-memory` before 2025.9.25

### The Attack
1. Memory MCP Server persists knowledge graph as JSONL to disk
2. Vulnerable version didn't validate `additionalProperties` — extra keys persisted silently
3. Attacker influences agent to configure Memory server to write to `.vscode/settings.json`
4. Agent calls `create_entities` with extra keys containing terminal hijacking payload
5. Agent never calls an explicit "write file" tool → bypasses file-write approval gates

### Why This Matters
- **Capability Laundering:** Calling one tool ("memory") produces effects of a different capability ("arbitrary file write")
- Controls gate tool invocations, not side effects
- Composability of MCP servers amplifies risk

**Fix:** PR #2726 — Strict schema validation + output sanitization (2025.9.25)

## MCPB Zip Slip & Silent Overwrite

### MCPB = ZIP archives with `.mcpb` extension

Three inherent ZIP risks for MCP client developers:
1. **Zip Slip (Path Traversal):** `../../../etc/passwd` entries. MCPB fixed in v0.2.6 (PR #74)
2. **Silent Overwrite:** Extracting silently overwrites `.bashrc`, `.vscode/settings.json`, etc.
3. **Symlink Attacks:** ZIP symlinks pointing outside extraction directory (CVE-2025-11001 in 7-Zip)

### CVE-2025-68143: Git MCP Server Credential Exfiltration
- Git MCP Server's `git_log` tool accepts arbitrary path arguments
- Attacker crafts request to read `.git/config` with embedded credentials
- Capability laundering: "version control" → credential theft
