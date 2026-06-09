###Method-Red
# 🛡️ Combined Red Team AI Arsenal — Complete Edition

> **A unified, end-to-end repository of AI-driven offensive security tools, skills, frameworks, and research.**
>
> 15 GitHub repos · 8 reference docs · 484+ AI skills · 275+ Decepticon skills · 79 reference files · 195 jailbreak guides · 4 categories · 1 mission.

---

## 📊 Complete Asset Inventory

### 🔴 Skill Libraries (Total: 131 skills)
| Repo | Skills | Lines of Tradecraft | Key Coverage |
|---|---|---|---|
| **Claude-Red** | 58 | Structured SKILL.md | Web (16), AD, Cloud, Mobile, IoT, Exploit Dev, Fuzzing, Wireless (14), AI, Recon, Auth, Infra |
| **Claude-BugHunter** | 71 | 681 disclosed-report patterns | All web bug classes, M365/Entra, Okta, vCenter, SSL-VPN, SharePoint, APK red-team, Web3, Supply-chain |
| **Claude-OSINT** | 2 paired (90+ modules) | 4,600+ lines | 48 secret-regex patterns, 80+ dorks, 9 credential validators, 27 attack-path templates |

### 🤖 Agent Frameworks (Total: 353 skills)
| Framework | Skills | Agents | Unique Capability |
|---|---|---|---|
| **red-run** (BLS) | 78 | 12 domain teammates | RAG skill routing (ChromaDB), SQLite state tracking, Agent teams, Retrospectives |
| **Decepticon** (PurpleAILAB) | 275 | Multi-agent | 15 LLM red-team plugins, APT emulation (APT29/28/33/34/41, FIN7, Lazarus, Sandworm, LockBit, Scattered Spider, Volt Typhoon), Soundwave engagement system |
| **RedteamAgent** (NeoTheCapt) | 31 methodologies + 79 refs | 8 agents | Multi-CLI support, containerized Kali, orchestrator GUI, streaming case pipeline |
| **redamon** | N/A (tool-based) | Fireteam parallel | 100+ tools, 185K detection rules, 400+ AI models, auto-PR with fixes |
| **PentestAgent** | N/A | MCP-compatible | LiteLLM multi-provider, Docker Kali, Playwright browser |
| **RedTeam-MCP** | N/A | 5 coordination modes | 68 providers, 1500+ models, Pipeline/Ensemble/Debate/Swarm/Hierarchical |
| **AI Red Team Crew** | N/A | 4 agents (CrewAI) | Llama 3.3/Cerebras, Streamlit GUI, hierarchical process |

### 🧠 Research & Threat Modeling
| Resource | Content |
|---|---|
| **AATMF** (v1+v2) | Adversarial AI Threat Modeling Framework — attack surfaces, threat actors, mitigations |
| **Spiritual Spell** | 195 jailbreak guides targeting Claude 3.7, 4, Opus 4.1-4.7, Claude Code, Amazon Rufus |
| **CVE-2025-54794** | Claude AI prompt injection via code blocks (CVSS 7.6) |

### 🛠️ Toolkits
| Toolkit | Content |
|---|---|
| **Red-Teaming-Toolkit** | Curated tools by attack phase: recon, initial access, delivery, situational awareness, credential dumping, privesc, defense evasion, persistence, lateral movement, exfiltration |
| **RedTeam-Tools** | PowerShell, AMSI bypass, payload hosting, lateral movement, reverse shells, post-exploitation, web pentest, privesc, credential harvesting, exfiltration, forensics, RE |

### 📚 Reference Docs (8)
| # | Document | Source |
|---|---|---|
| 1 | CVE-2025-54794 & 54795: InversePrompt | Cymulate |
| 2 | Comment and Control: Prompt Injection → Credential Theft | oddguan.com |
| 3 | Constitutional Classifiers: Jailbreak Defense | Anthropic (arXiv: 2501.18837) |
| 4 | red-run: Architecture & Philosophy | Black Lantern Security |
| 5 | Anthropic Bug Bounty Programs | Bugcrowd/HackerOne |
| 6 | CVE-2025-53109 & 53110: EscapeRoute | Cymulate |
| 7 | Agent SkillSlip: Path Traversal in AI Skill Installers | oddguan.com |
| 8 | Capability Laundering in MCP + MCPB Zip Slip | oddguan.com |
| — | arXiv:2501.18837 Constitutional Classifiers paper | Anthropic |

---

## 🔄 Complete End-to-End Capability Coverage

### Phase 1: PRE-ENGAGEMENT & PLANNING
| Capability | Source | Format |
|---|---|---|
| Threat modeling framework | AATMF v1+v2 | Markdown framework |
| Engagement scoping | Decepticon Soundwave (roe-template, conops-template, threat-profile) | 17 SKILL.md files |
| APT adversary emulation profiles | Decepticon (29/28/33/34/41, FIN7, Lazarus, Sandworm, LockBit, Scattered Spider, Volt Typhoon) | 10+ APT emulation skills |
| Rules of engagement | Decepticon Soundwave (roe-template, validation-checklist) | Structured templates |
| Data handling protocols | Decepticon Soundwave data-handling-template | Template |
| Contact/abort procedures | Decepticon Soundwave (contact-template, abort-template) | Templates |
| Red team mindset | Claude-BugHunter (redteam-mindset) | SKILL.md |
| Bug bounty methodology | Claude-BugHunter (bb-methodology) | SKILL.md |
| OSINT methodology | Claude-OSINT, Claude-BugHunter, Claude-Red | Multi-source |

### Phase 2: RECONNAISSANCE & DISCOVERY
| Capability | Source | Coverage |
|---|---|---|
| Subdomain enumeration (8+ sources) | Claude-OSINT | crt.sh, DNS bruteforce, 7-source fallback |
| DNS/WHOIS/RDAP/historical WHOIS | Claude-OSINT | Full pipeline |
| ASN/IP correlation (Cymru/RIPEstat/bgp.tools) | Claude-OSINT | Bulk IP→ASN mapping |
| Email/people OSINT | Claude-BugHunter, Claude-OSINT | Identity fabric mapping |
| M365/Entra tenant fingerprinting | Claude-OSINT, Claude-BugHunter | GUID extraction, Teams federation |
| Okta tenant enumeration | Claude-OSINT, Claude-BugHunter | /api/v1/authn user-enum |
| AWS account-ID extraction | Claude-OSINT | Headers + ARN regex |
| Google Workspace OIDC discovery | Claude-OSINT | Full enumeration |
| ADFS/SAML/OIDC fingerprinting | Claude-OSINT | Multi-provider |
| GraphQL/Swagger/OpenAPI discovery | Claude-OSINT | 13+28 paths |
| JS deep analysis + sourcemap leakage | Claude-OSINT | Internal-host regex |
| Subdomain takeover detection | Claude-OSINT | 27 providers |
| Secret scanning (48 patterns) | Claude-OSINT, Claude-BugHunter | High-entropy regex |
| Credential validation (9 validators) | Claude-OSINT | Read-only checks |
| Wayback CDX mining | Claude-OSINT | Legacy app pivots |
| Supply chain recon | Claude-BugHunter (supply-chain-attack-recon) | Full chain mapping |
| Passive cloud recon | Decepticon (cloud-recon) | IP ranges, naming patterns |
| Web tech stack fingerprinting | red-run (web-discovery), Decepticon (web-recon) | Multi-tool |
| Network recon (Nmap/masscan) | red-run (network-recon) | Full port/service |
| SMB enumeration | red-run (smb-enumeration) | Shares, users, ACLs |
| Database enumeration | red-run (database-enumeration) | Multi-DB |
| Infrastructure enumeration | red-run (infrastructure-enumeration) | Services, versions |
| XMPP enumeration | red-run (xmpp-enumeration) | Chat services |
| Remote access enumeration | red-run (remote-access-enumeration) | RDP, SSH, VNC |
| Active Directory discovery | red-run (ad-discovery), Decepticon (BloodHound) | Full AD mapping |
| Container/K8s recon | Claude-BugHunter (hunt-k8s), red-run | Docker, K8s API |
| CI/CD pipeline recon | Claude-BugHunter (hunt-cicd) | GitHub Actions, Jenkins |
| Source code review | red-run (source-code-review) | Patterns, secrets |
| Cloud IAM enumeration | Claude-BugHunter (cloud-iam-deep) | Multi-cloud |

### Phase 3: VULNERABILITY ANALYSIS
| Capability | Source | Coverage |
|---|---|---|
| SQL Injection (Error/Blind/Union/Stacked) | red-run (4 skills), Claude-Red, Claude-BugHunter | Full variants |
| NoSQL Injection | red-run, Claude-BugHunter | MongoDB, etc. |
| LDAP Injection | red-run, Claude-BugHunter | Full exploitation |
| XSS (Reflected/Stored/DOM) | red-run (3 skills), Claude-Red, Claude-BugHunter | All contexts |
| CSRF | red-run, Claude-BugHunter | Full bypasses |
| CORS misconfiguration | red-run, Claude-BugHunter | Advanced exploitation |
| SSRF | red-run, Claude-Red, Claude-BugHunter | Full chain: SSRF→RCE |
| XXE | red-run, Claude-Red, Claude-BugHunter | OOB, error-based |
| SSTI (Jinja2/Freemarker/Twig) | red-run (3 skills), Claude-Red, Claude-BugHunter | Language-specific |
| Command Injection | red-run, Claude-BugHunter, Decepticon | OS command, code injection |
| PHP/Python Code Injection | red-run (2 skills) | Language-specific |
| File Upload Bypass | red-run, Claude-Red, Claude-BugHunter | Extension, content-type, magic bytes |
| Path Traversal / LFI | red-run, Claude-BugHunter, Decepticon | Full bypass chain |
| IDOR | red-run, Claude-Red, Claude-BugHunter | Horizontal + vertical |
| Race Condition | red-run, Claude-Red, Claude-BugHunter | TOCTOU, limit-overrun |
| Deserialization (.NET/Java/PHP) | red-run (3 skills), Claude-Red, Claude-BugHunter, Decepticon | Language-specific |
| HTTP Request Smuggling | red-run, Claude-Red, Claude-BugHunter | CL.TE, TE.CL, TE.TE |
| GraphQL Attacks | Claude-Red, Claude-BugHunter | Introspection, batching, depth bypass |
| OAuth 2.0 Attacks | Claude-Red, Claude-BugHunter, red-run | redirect_uri, CSRF, PKCE bypass |
| JWT Attacks | Claude-Red, red-run | None algo, HMAC confusion, kid injection |
| SAML Attacks | Claude-BugHunter | XML signature wrapping, Golden SAML |
| Open Redirect | Claude-Red, Claude-BugHunter | Full bypass |
| Business Logic | Claude-Red, Claude-BugHunter, Decepticon | Workflow abuse |
| Prototype Pollution | Decepticon | Client/server-side |
| WebSocket Attacks | Claude-BugHunter | CSWSH, injection |
| gRPC Attacks | Claude-BugHunter | Reflection, injection |
| Host Header Injection | Claude-BugHunter | Password reset poisoning |
| Cache Poisoning | Claude-BugHunter | Web cache deception |
| Browser Exploitation | red-run | Client-side attacks |
| LLM/AI Security (15 techniques) | Decepticon (t01-t15), Claude-BugHunter (hunt-llm-ai) | Prompt injection, RAG poisoning, agentic exploit, multimodal, training poisoning, output exfil, deception, supply chain, infra warfare, human-AI coupling, memory manipulation, reasoning exploit, linguistic evasion, API exploitation, confidentiality breach |
| Bug identification | Claude-Red (fuzzing skills) | Crash analysis, vuln classes |
| WAF bypass | Claude-Red | Multi-WAF evasion |
| ASP.NET specific | Claude-BugHunter | ViewState, WebResource |
| Laravel specific | Claude-BugHunter | Debug mode, .env exposure |
| Next.js specific | Claude-BugHunter | SSG/SSR edge cases |
| Node.js specific | Claude-BugHunter | Prototype pollution, desync |
| Spring Boot specific | Claude-BugHunter | Actuator, H2 console |
| Session management | Claude-BugHunter | Fixation, prediction, JWT |
| ATO (Account Takeover) | Claude-BugHunter | Full chain |
| Auth bypass | Claude-BugHunter, Decepticon | Multi-technique |
| MFA bypass | Claude-BugHunter | Push fatigue, backup codes |
| 2FA bypass | red-run | SMS, TOTP, recovery |
| Brute force | Claude-BugHunter | Rate limiting bypass |
| TLS/Network | Claude-BugHunter | Certificate issues, downgrade |
| Source leak | Claude-BugHunter | .git, .env, backup files |
| NTLM info leak | Claude-BugHunter | NTLM relay prep |
| DOM-based bugs | Claude-BugHunter | postMessage, DOM clobbering |
| Meme coin / Web3 audit | Claude-BugHunter | Solidity, smart contracts |
| APK red team pipeline | Claude-BugHunter | Static + dynamic analysis |
| SharePoint exploitation | Claude-BugHunter | ToolShell, legacy SOAP |
| Tomcat Manager deploy | red-run | WAR deployment |
| AJP Ghostcat | red-run | CVE-2020-1938 |

### Phase 4: EXPLOITATION & INITIAL ACCESS
| Capability | Source | Coverage |
|---|---|---|
| Enterprise VPN exploitation | Claude-BugHunter | Cisco, Fortinet, Citrix, Palo Alto, Pulse, SonicWall, F5 |
| VMware vCenter exploitation | Claude-BugHunter | Full vCenter attack chain |
| M365/Entra ID attack | Claude-BugHunter | OAuth, device-code phishing, Teams federation |
| Okta-as-IdP attack | Claude-BugHunter | Full IdP compromise |
| Initial access vectors | Claude-Red (offensive-initial-access) | Phishing, macros, payloads |
| Exploit development | Claude-Red (6 exploit-dev skills) | Basic, advanced, course, mitigations, TOCTOU, crash analysis |
| Fuzzing | Claude-Red (4 fuzzing skills) | Bug identification, course, vuln classes |
| Web exploit ops | red-run (web-exploit-agent) | Full web exploitation |
| AD exploit ops | red-run (ad-exploit-agent) | Full AD exploitation |
| Linux exploit | red-run (web-exploit, linux-privesc) | Full Linux exploitation |
| Decepticon Exploit (66 skills) | Decepticon | Comprehensive web/network exploit library |

### Phase 5: POST-EXPLOITATION & PRIVILEGE ESCALATION
| Capability | Source | Coverage |
|---|---|---|
| **Linux Privilege Escalation** | | |
| Linux discovery | red-run, Decepticon | Users, groups, network, processes |
| Sudo/SUID/Capabilities abuse | red-run | Full GTFObin coverage |
| Cron/service abuse | red-run | Writable cron, systemd timers |
| File path abuse | red-run | PATH hijacking, library injection |
| Kernel exploits | red-run | Dirty COW, OverlayFS, etc. |
| Container escapes | red-run | Docker, K8s breakout |
| **Windows Privilege Escalation** | | |
| Windows discovery | red-run, Decepticon | Users, groups, patches, services |
| Service/DLL abuse | red-run | Unquoted paths, weak permissions |
| Token impersonation | red-run | SeImpersonate, potato attacks |
| UAC bypass | red-run | Multi-technique |
| Kernel exploits | red-run | Full Windows kernel |
| Credential harvesting | red-run | LSASS dumping, SAM extraction |
| **Active Directory** | | |
| AD discovery | red-run, Decepticon | BloodHound, manual enumeration |
| Kerberos roasting | red-run, Decepticon | AS-REP, Kerberoasting |
| Kerberos delegation abuse | red-run | Unconstrained, constrained, RBCD |
| Kerberos ticket forging | red-run | Golden/Silver ticket |
| Pass-the-Hash | red-run | NTLM relay, PtH |
| ACL abuse | red-run | DACL, Owner, AdminSDHolder |
| ADCS abuse | red-run (3 skills), Decepticon | ESC1-13, template abuse, persistence |
| GPO abuse | red-run | GPO deployment |
| Auth coercion + relay | red-run | PrinterBug, PetitPotam, DFSCoerce |
| SCCM exploitation | red-run | NAA, site takeover |
| Trust attacks | red-run | Domain/forest trust abuse |
| Credential dumping | red-run | LSASS, NTDS.dit, SAM, LSA secrets |
| AD persistence | red-run | Golden ticket, Skeleton Key, DCShadow |
| DCSync | Decepticon | Replication abuse |
| LAPS | Decepticon | LAPS password extraction |
| NTLM relay | Decepticon | Full relay chain |
| **Password Attacks** | | |
| Password spraying | red-run, Decepticon | Domain, O365, ADFS |
| Credential cracking | red-run, Decepticon | Hashcat, John |
| Credential recovery | red-run | Browser, RDP, Wi-Fi passwords |
| **Defense Evasion** | | |
| AV/EDR evasion | red-run, Claude-Red, Claude-BugHunter | AMSI bypass, ETW patching, unhooking |
| Application whitelist bypass | Claude-Red | LOLBins, signed script proxy |
| OPSEC discipline | Decepticon (opsec, stealth-infra) | Full operational security |
| Shellcode development | Claude-Red | Custom shellcode, encoding |
| Windows boundaries/mitigations | Claude-Red | Session isolation, AppContainer |
| AMSI bypass techniques | Decepticon, RedTeam-Tools | PowerShell, .NET, VBA |
| **Lateral Movement** | | |
| SMB exploitation | red-run | PSExec, WMI, DCOM |
| Pivoting & tunneling | red-run | SSH, chisel, ligolo, SOCKS |
| Lateral movement toolbox | Red-Teaming-Toolkit, RedTeam-Tools | Impacket, CME, Evil-WinRM |
| **C2 Integration** | | |
| Sliver C2 | red-run, Decepticon | Full C2 integration |
| Red team infrastructure | Decepticon | Domain fronting, redirectors |

### Phase 6: DATA EXFILTRATION & PERSISTENCE
| Capability | Source | Coverage |
|---|---|---|
| Exfiltration | Red-Teaming-Toolkit, RedTeam-Tools | DNS, ICMP, HTTP/S |
| AD persistence | red-run, Decepticon | Multi-technique |
| Desktop persistence | Decepticon, RedTeam-Tools | Registry, scheduled tasks, WMI |
| Stealth infrastructure | Decepticon | Redirectors, CDN, domain fronting |
| Evasion techniques | Claude-Red, red-run, Decepticon | Full arsenal |

### Phase 7: REPORTING & RETROSPECTION
| Capability | Source | Coverage |
|---|---|---|
| Bug bounty reporting | Claude-BugHunter (report-writing, bugcrowd-reporting) | VRT-aware severity, 7-Question Gate |
| Red team report template | Claude-BugHunter (redteam-report-template) | Full deliverable |
| Evidence hygiene | Claude-BugHunter | PII redaction, screenshot standards |
| Finding protocol | Decepticon (finding-protocol, verifier) | Verification, severity |
| Triage & validation | Claude-BugHunter (triage-validation) | OOS rebuttals, chain verification |
| Retrospective analysis | red-run (retrospective) | Skill improvement, gap identification |
| Post-engagement cleanup | Decepticon Soundwave (cleanup-template) | Full cleanup procedures |
| Red team reporting | Claude-Red (offensive-reporting) | Structured reporting |
| Mid-engagement IR detection | Claude-BugHunter | Blue team awareness |

### Phase 8: SPECIALIZED DOMAINS
| Capability | Source | Coverage |
|---|---|---|
| **Wireless** | | |
| Wi-Fi recon | Claude-Red (offensive-wifi-recon) | Full 802.11 discovery |
| WPA2-PSK attacks | Claude-Red, Decepticon | Handshake capture, cracking |
| WPA3-SAE attacks | Claude-Red, Decepticon | Dragonblood, downgrade |
| WPA Enterprise (EAP) | Claude-Red, Decepticon | RADIUS, EAP-TTLS, EAP-PEAP |
| Evil Twin / KARMA | Claude-Red, Decepticon | Full rogue AP |
| WPS attacks | Claude-Red, Decepticon | Pixie Dust, PIN bruteforce |
| Deauth/Disassociation | Claude-Red, Decepticon | PMF bypass |
| KRACK/FragAttacks | Claude-Red, Decepticon | Protocol-level attacks |
| Bluetooth (BLE + Classic) | Claude-Red (2 skills) | Full BT attack surface |
| LoRaWAN/Sub-GHz | Claude-Red | IoT wireless |
| Zigbee/Thread/Matter | Claude-Red | Smart home protocols |
| Z-Wave | Claude-Red | Home automation |
| **Mobile** | | |
| Mobile app testing | Claude-Red (offensive-mobile) | Android + iOS |
| APK red team pipeline | Claude-BugHunter | Full APK analysis |
| iOS static analysis | Decepticon (reverser/ios-static) | IPA, Mach-O |
| **IoT & Embedded** | | |
| IoT assessment | Claude-Red (offensive-iot) | Firmware, hardware, protocols |
| Firmware analysis | Decepticon (reverser/firmware) | Extraction, emulation |
| **Cloud** | | |
| Cloud security assessment | Claude-Red (offensive-cloud) | AWS, Azure, GCP |
| Cloud IAM deep | Claude-BugHunter (cloud-iam-deep) | Cross-account, federation |
| Cloud misconfig | Claude-BugHunter (hunt-cloud-misconfig) | Storage, services |
| **Reverse Engineering** | | |
| Malware triage | Decepticon (reverser/malware-triage) | Static + dynamic |
| Packer unpacking | Decepticon (reverser/packer-unpacking) | Multi-packer |
| Anti-debug bypass | Decepticon (reverser/anti-debug-bypass) | Windows, Linux, macOS |
| ROP chain analysis | Decepticon (reverser/rop-chain) | Exploit dev support |
| Ghidra deep analysis | Decepticon (reverser/ghidra) | Scripting, automation |
| YARA rule hunting | Decepticon (reverser/yara-hunting) | Rule creation |
| CTF binary triage | Decepticon (reverser/ctf-triage, triage) | Quick analysis |
| Fuzzing integration | Decepticon (reverser/fuzzing) | AFL++, libFuzzer |
| **AI/ML Red Teaming** | | |
| LLM red team (15 techniques) | Decepticon (t01-t15) | Full OWASP LLM + beyond |
| AI security | Claude-Red (offensive-ai-security) | Model, pipeline, deployment |
| Adversarial ML evasion | Decepticon | Model poisoning, evasion |
| Prompt injection (comprehensive) | Decepticon, Claude-BugHunter, CVE writeups | Direct, indirect, multimodal |
| RAG poisoning | Decepticon | Knowledge base corruption |
| Agentic exploit | Decepticon | Tool use hijacking |
| AI supply chain | Decepticon | Model, data, dependency |
| **Jailbreak Techniques (195 guides)** | Spiritual Spell Red Teaming | |
| Claude 3.7 | Spiritual Spell | Chain of Draft jailbreak |
| Claude 4 (Sonnet) | Spiritual Spell | ENI, Loki variants |
| Opus 4.1 | Spiritual Spell | Multiple variants |
| Opus 4.5 | Spiritual Spell | ENI LIME (current strongest) |
| Opus 4.6 | Spiritual Spell | ENI LIME, ENI Smol, be-You, Simple Break |
| Opus 4.7 | Spiritual Spell | ENI LIME (Apr) |
| Claude Code | Spiritual Spell | ENI Lite, CLAUDE.md injection |
| Amazon Rufus | Spiritual Spell | Full system prompt, ENI Zoomer |

---

## 🔗 Complete Link Map — All Discovered Resources

### Primary GitHub Repos (15)
1. [SnailSploit/Claude-Red](https://github.com/SnailSploit/Claude-Red)
2. [elementalsouls/Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter)
3. [elementalsouls/Claude-OSINT](https://github.com/elementalsouls/Claude-OSINT)
4. [blacklanternsecurity/red-run](https://github.com/blacklanternsecurity/red-run)
5. [NeoTheCapt/RedteamAgent](https://github.com/NeoTheCapt/RedteamAgent)
6. [samugit83/redamon](https://github.com/samugit83/redamon)
7. [GH05TCREW/pentestagent](https://github.com/GH05TCREW/pentestagent)
8. [RedTeamMCP/RedTeam-MCP](https://github.com/RedTeamMCP/RedTeam-MCP)
9. [PurpleAILAB/Decepticon](https://github.com/PurpleAILAB/Decepticon)
10. [patelankit706/redteamagent](https://github.com/patelankit706/redteamagent)
11. [SnailSploit/AATMF](https://github.com/SnailSploit/AATMF-Adversarial-AI-Threat-Modeling-Framework)
12. [Goochbeater/Spiritual-Spell-Red-Teaming](https://github.com/Goochbeater/Spiritual-Spell-Red-Teaming)
13. [AdityaBhatt3010/CVE-2025-54794](https://github.com/AdityaBhatt3010/CVE-2025-54794-Hijacking-Claude-AI-with-a-Prompt-Injection-The-Jailbreak-That-Talked-Back)
14. [infosecn1nja/Red-Teaming-Toolkit](https://github.com/infosecn1nja/Red-Teaming-Toolkit)
15. [elinakrmova/RedTeam-Tools](https://github.com/elinakrmova/RedTeam-Tools)

### Research & Blog Posts (7)
| # | URL | Topic |
|---|---|---|
| 1 | [blog.blacklanternsecurity.com/p/red-run](https://blog.blacklanternsecurity.com/p/red-run) | red-run architecture deep-dive |
| 2 | [anthropic.com/research/constitutional-classifiers](https://www.anthropic.com/research/constitutional-classifiers) | Jailbreak defense system |
| 3 | [cymulate.com — InversePrompt](https://cymulate.com/blog/cve-2025-547954-54795-claude-inverseprompt) | CVE-2025-54794 & 54795 |
| 4 | [cymulate.com — EscapeRoute](https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic) | CVE-2025-53109 & 53110 |
| 5 | [oddguan.com — Comment and Control](https://oddguan.com/blog/comment-and-control-prompt-injection-credential-theft-claude-code-gemini-cli-github-copilot) | Cross-vendor prompt injection |
| 6 | [oddguan.com — Agent SkillSlip](https://oddguan.com/blog/agent-skillslip/) | Path traversal in AI skill installers |
| 7 | [oddguan.com — MCPB Zip Slip](https://oddguan.com/blog/mcp-bundle-security-zip-slip-overwrite-for-mcp-client/) | ZIP security in MCP bundles |

### Additional Research Found Through Links
| # | URL | Topic |
|---|---|---|
| A | [oddguan.com — Capability Laundering](https://oddguan.com/blog/anthropic-memory-mcp-server-terminal-hijacking-capability-laundering/) | Memory MCP Server → Terminal hijacking |
| B | [oddguan.com — CVE-2025-68143](https://oddguan.com/blog/anthropic-mcp-server-git-credential-exfiltration-capability-laundering-cve-2025-68143/) | Git MCP Server credential exfiltration |
| C | [arXiv:2501.18837](https://arxiv.org/abs/2501.18837) | Constitutional Classifiers paper |
| D | [HackerOne: Constitutional Classifiers](https://hackerone.com/constitutional-classifiers) | Bug bounty program |
| E | [xbow.com](https://xbow.com/blog/xbow-on-hackerone-whats-next) | Referenced in red-run blog |
| F | [dreadnode.io](https://dreadnode.io/research) | Referenced in red-run blog |
| G | [Haize Labs](https://www.haizelabs.com/) | Constitutional Classifiers red team |
| H | [Gray Swan](https://www.grayswan.ai/) | Constitutional Classifiers red team |
| I | [UK AI Safety Institute](https://www.aisi.gov.uk/) | Constitutional Classifiers red team |

### Additional CVEs Documented
| CVE | Product | Type | CVSS |
|---|---|---|---|
| CVE-2025-54794 | Claude Code | Path restriction bypass | 7.7 |
| CVE-2025-54795 | Claude Code | Command injection | 8.7 |
| CVE-2025-53109 | Filesystem MCP Server | Symlink bypass → code execution | High |
| CVE-2025-53110 | Filesystem MCP Server | Directory containment bypass | High |
| CVE-2025-68143 | Git MCP Server | Credential exfiltration | — |
| CVE-2025-61590 | Cursor | VS Code config injection | — |

---

## 📁 Repository Structure

```
combined-redteam/
├── README.md                                    ← THIS FILE
├── .gitignore
├── skill-libraries/
│   ├── Claude-Red/                             58 skills · 14 categories
│   ├── Claude-BugHunter/                       71 skills · 681 disclosed patterns
│   └── Claude-OSINT/                           2 skills (90+ modules) · 4,600+ lines
├── agent-frameworks/
│   ├── red-run/                                78 skills · 12 agents · RAG routing
│   ├── RedteamAgent/                           8 agents · 79 references · Orchestrator GUI
│   ├── redamon/                                100+ tools · 185K+ rules · Fireteam mode
│   ├── PentestAgent/                           MCP-compatible · LiteLLM
│   ├── RedTeam-MCP/                            68 providers · 1500+ models · 5 modes
│   ├── Decepticon/                             275 skills · APT emulation · Web dashboard
│   └── redteamagent/                           CrewAI + Cerebras Llama · Streamlit
├── threat-modeling/
│   └── AATMF/                                  v1 (2023) + v2 (2025)
├── jailbreak-research/
│   └── Spiritual-Spell-Red-Teaming/            195 guides · Claude 3.7→4.7 · Opus 4.1→4.7
├── cve-research/
│   └── CVE-2025-54794/                         Claude AI prompt injection PoC
├── red-team-toolkits/
│   ├── Red-Teaming-Toolkit/                    300+ tools by attack phase
│   └── RedTeam-Tools/                          Practical pentest tools
└── reference-docs/
    ├── cve-2025-54794-54795-inverseprompt.md
    ├── cve-2025-53109-53110-escaperoute.md
    ├── comment-and-control-prompt-injection.md
    ├── agent-skillslip-path-traversal.md
    ├── capability-laundering-and-mcpb-zip-slip.md
    ├── constitutional-classifiers.md
    ├── red-run-blog.md
    └── anthropic-bug-bounty.md
```

---

## 🚀 Quick Start Paths

### Path A: Skills-Only (Lightest)
```bash
cd skill-libraries/Claude-Red && bash install.sh
cd ../Claude-BugHunter && bash scripts/install.sh --all
cd ../Claude-OSINT && cp -r skills/* ~/.claude/skills/
```

### Path B: Full Orchestrator (red-run)
```bash
cd agent-frameworks/red-run
bash install.sh && bash preflight.sh && bash run.sh
```

### Path C: One-Command (Decepticon)
```bash
curl -fsSL https://decepticon.red/install | bash
decepticon onboard && decepticon
```

### Path D: Multi-Agent (RedteamAgent)
```bash
cd agent-frameworks/RedteamAgent && bash install.sh
```

### Path E: MCP Hub (RedTeam-MCP)
```bash
cd agent-frameworks/RedTeam-MCP
pip install -r requirements.txt && python main.py
```

---

## 📊 Complete Stats

| Metric | Count |
|---|---|
| **Total GitHub Repos** | 15 |
| **Total AI Skills (all repos)** | 484+ |
| **Decepticon Skills** | 275 |
| **red-run Skills** | 78 |
| **Claude-BugHunter Skills** | 71 |
| **Claude-Red Skills** | 58 |
| **Claude-OSINT Skills** | 2 (90+ modules) |
| **Reference Files (RedteamAgent)** | 79 |
| **Jailbreak Guides (Spiritual Spell)** | 195 |
| **Reference Documents** | 8 |
| **Additional Research URLs** | 9 |
| **CVEs Documented** | 6+ |
| **AI Models Supported** | 1500+ |
| **Coordination Modes** | 5+ |
| **Security Tools Referenced** | 400+ |
| **APTs Emulated** | 10+ |
| **Disclosed Report Patterns** | 681 |

---

## ⚠️ Critical Safety Warnings

1. **Authorized use only.** These tools are for CTFs, labs, authorized engagements, and security research.
2. **Data exfiltration risk.** Cloud-based LLM APIs receive your data. Use DLP-safe modes where available.
3. **Zero OPSEC by default.** Agentic tools have no operational security awareness.
4. **Non-deterministic output.** Same input ≠ same output. Human operator must supervise.
5. **Prompt injection is unsolved.** As demonstrated by Comment and Control, SkillSlip, and Capability Laundering research.

---

## 📄 License

Each sub-repository retains its original license. See individual LICENSE files. Reference documents are attributed to original authors.

---

*Compiled from the AI red-teaming ecosystem. For authorized security research, CTF training, and defensive improvement only.*
