from crewai import Task

class RedTeamTasks:
    def recon_task(self, agent, target, mission_dir):
        report_file = f"{mission_dir}/recon_report.md"
        return Task(
            description=f"""
                [ROLE]
                You are a Reconnaissance Operator. Your execution must be flawless and methodical.

                [OBJECTIVE]
                Gather intelligence on the target '{target}' and create a detailed log of all findings in the report file `{report_file}`.

                [CRITICAL INSTRUCTIONS]
                You MUST follow this sequence precisely. After EVERY tool execution, you MUST IMMEDIATELY use the `File Append Tool` to log the complete, raw output to `{report_file}`.

                1.  **Target Analysis:**
                    - If '{target}' is a domain, use `Resolve Domain to IP` tool.
                    - **Log the output to `{report_file}`.**
                    - If '{target}' is a domain, use `Whois Lookup Tool`.
                    - **Log the output to `{report_file}`.**

                2.  **Network Enumeration:**
                    - Identify the primary IP address of the target.
                    - Execute `Nmap Port Scanner` on this IP.
                    - **Log the full Nmap output to `{report_file}`.**

                3.  **Vulnerability Research (MANDATORY):**
                    - Analyze the Nmap output to identify services and version numbers (e.g., 'Apache httpd 2.4.52', 'OpenSSH 8.2p1').
                    - For EACH discovered service/version, execute the `SerperDevTool` or available web scraping tools to search for known public vulnerabilities or exploits. Use search queries like "[service name] [version] exploit" or "[service name] [version] vulnerability".
                    - **Log every search query and its results to `{report_file}`.** This is non-negotiable.

                4.  **Web Enumeration:**
                    - If web ports (e.g., 80, 443) were found, execute `GoBuster Directory and File Brute-forcer` on the target '{target}'.
                    - **Log the full GoBuster output to `{report_file}`.**

                Your final output for this task must be a simple confirmation message.
            """,
            expected_output=f"Confirmation that all reconnaissance steps were completed and all tool outputs were logged to `{report_file}`.",
            agent=agent
        )

    def exploit_task(self, agent, context, mission_dir):
        recon_report_file = f"{mission_dir}/recon_report.md"
        exploit_report_file = f"{mission_dir}/exploit_report.md"
        return Task(
            description=f"""
                [ROLE]
                You are an Exploitation Operator. Your task is to breach the target.

                [OBJECTIVE]
                Based on intelligence from `{recon_report_file}`, gain initial access to the target and log all actions in `{exploit_report_file}`.

                [CRITICAL INSTRUCTIONS]
                You MUST follow this sequence. After EVERY tool execution, you MUST IMMEDIATELY use the `File Append Tool` to log the complete, raw output to `{exploit_report_file}`.

                1.  **Intelligence Review:**
                    - Read the `{recon_report_file}` to identify potential vulnerabilities. Pay close attention to the vulnerability research section.

                2.  **Exploit Verification (MANDATORY):**
                    - Based on the most promising vulnerability in the recon report, use the `SerperDevTool` or available web scraping tools to find a specific, detailed proof-of-concept (PoC) or tutorial for the exploit. You need to understand how the exploit works before attempting it.
                    - **Log your search query and the PoC details to `{exploit_report_file}`.**

                3.  **Attack Execution:**
                    - Select the correct tool for the verified exploit (e.g., `SQLMap`, `Metasploit Executor`, `SSH Bruteforce Tool`).
                    - Execute the attack.
                    - **Log the full output of the attack tool, including the command used and the result (success or failure), to `{exploit_report_file}`.**

                4.  **Contingency:**
                    - If your first attempt fails, return to step 1, select the next most promising vulnerability, and repeat the entire process.

                Your final output for this task must be a brief summary of the outcome.
            """,
            expected_output=f"A brief summary of the exploitation outcome (e.g., 'SUCCESS: Gained shell via SQLMap') and confirmation that all actions were logged to `{exploit_report_file}`.",
            agent=agent,
            context=[context]
        )
    
    def privesc_task(self, agent, context, mission_dir):
        report_file = f"{mission_dir}/privesc_report.md"
        return Task(
            description=f"""
                [ROLE]
                You are a Post-Exploitation Operator. You are inside the system.

                [OBJECTIVE]
                Elevate privileges to root and log all actions in the report file `{report_file}`.

                [CRITICAL INSTRUCTIONS]
                You MUST follow this sequence. After EVERY tool execution, you MUST IMMEDIATELY use the `File Append Tool` to log the complete, raw output to `{report_file}`.

                1.  **System Enumeration:**
                    - Execute the `LinPEAS Executor` tool.
                    - **Log the full, raw output to `{report_file}`.**

                2.  **Sensitive Data Search:**
                    - Execute the `File System Search` tool for keywords like 'password', 'config', 'id_rsa', 'secret', '.env'.
                    - **Log the full, raw output of the search to `{report_file}`.**

                3.  **Escalation Analysis:**
                    - Review the tool outputs you have logged. Append a final markdown section to `{report_file}` titled `## Privilege Escalation Analysis`.
                    - In this section, clearly state the chosen escalation vector and why you chose it.

                Your final output must be a simple confirmation of the outcome.
            """,
            expected_output=f"A confirmation message stating the outcome of the privilege escalation attempt and that all findings have been logged to `{report_file}`.",
            agent=agent,
            context=[context]
        )

    # def reporting_task(self, agent, context, mission_dir):
    #     # This task remains largely the same, as its job is simple compilation.
    #     # A direct prompt works well here.
    #     return Task(
    #         description=f"""
    #             [ROLE]
    #             You are the Red Team Operations Coordinator.

    #             [OBJECTIVE]
    #             Compile the final, unabridged attack narrative from all operational reports.

    #             [CRITICAL INSTRUCTIONS]
    #             1. Read the following files from the mission directory `{mission_dir}`:
    #                - `recon_report.md`
    #                - `exploit_report.md`
    #                - `privesc_report.md`
    #             2. Combine their contents into a single markdown file.
    #             3. The final report MUST use the following structure, preserving ALL raw data:
    #                - `# Red Team Final Report: [Target]`
    #                - `## Phase 1: Reconnaissance`
    #                - `## Phase 2: Initial Access`
    #                - `## Phase 3: Privilege Escalation`

    #             Your final output is the complete, combined markdown report.
    #         """,
    #         expected_output=f"The final, complete markdown report, combining all findings from the files in `{mission_dir}`.",
    #         agent=agent,
    #         context=context
    #     )

    def reporting_task(self, agent, context, mission_dir):
        # This task remains largely the same, as its job is simple compilation.
        # A direct prompt works well here.
        return Task(
            description=f"""
                [ROLE]
                You are the Red Team Operations Coordinator.

                [OBJECTIVE]
                Compile the final, unabridged attack narrative from all operational reports.

                [CRITICAL INSTRUCTIONS]
                1. Read the following files from the mission directory `{mission_dir}`:
                   - `recon_report.md`
                   - `exploit_report.md`
                   - `privesc_report.md`
                2.  Synthesize all the information into a single, cohesive, and detailed report.
                3.  The report must follow a clear narrative structure: Introduction, Initial Reconnaissance, Gaining Access, and Privilege Escalation.
                4.  **Do not summarize.** Include all the technical details, tool outputs, and commands from the individual reports.
                5.  The final report should be a comprehensive story of how the target was compromised from start to finish.
                6.  **Do NOT include any recommendations or remediation advice.** Focus solely on the attack path and findings.
            """,
            expected_output=f"""
                A single, final, detailed markdown report that combines all findings from the files in `{mission_dir}`.
                The report must be an exhaustive attack narrative, including all technical details.
            """,
            agent=agent,
            context=context
        )