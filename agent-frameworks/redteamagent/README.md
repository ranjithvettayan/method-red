# 🤖 AI Red Team Crew

An autonomous, AI-powered multi-agent system designed to simulate cybersecurity red team engagements. This platform leverages the power of **CrewAI**, **Cerebras Inference API** and **Llama 3.3** to automate the entire attack lifecycle, from reconnaissance to privilege escalation, all managed through a clean **Streamlit** user interface.

![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)  ![License](https://img.shields.io/badge/License-Apache-green.svg)  ![Framework](https://img.shields.io/badge/Framework-CrewAI-orange.svg)  ![Model](https://img.shields.io/badge/Model-Llama_3.3-violet.svg)  ![API](https://img.shields.io/badge/API-Cerebras-red.svg)

## 🎥 Demo Video

[![AI Red Team Crew Demo Video](https://img.youtube.com/vi/tV_K_LI0e1s/hqdefault.jpg)](https://youtu.be/tV_K_LI0e1s)

*(Click the image above to watch a video demonstration of the platform in action)*

---

## ✨ Core Features

*   **🤖 Autonomous Agent System:** Utilizes a crew of specialized AI agents (Coordinator, Recon, Exploitation, Post-Exploitation) that work together to achieve their objectives.
*   **🚀 Powered by Cerebras Llama 3.3 API:** Leverages the advanced reasoning capabilities of the Llama 3.3 70b model (via the high-speed Cerebras API) for intelligent decision-making.
*   **🖥️ Interactive GUI:** A user-friendly Streamlit interface for configuring targets, launching missions, and viewing results in real-time.
*   **📝 Live Logging & Reporting:** Watch the agents work in real-time with a live log stream and receive a detailed, automatically-generated final report detailing the entire attack narrative.
*   **🛠️ Real Tools, Real Results:** Integrates and orchestrates real-world cybersecurity tools like `Nmap`, `GoBuster`, `Whois`, and more to perform its tasks.
*   **🧠 Intelligent Web Search:** Agents actively use web search to research potential vulnerabilities for discovered services, mimicking a key step in a real operator's workflow.

---

## ⚙️ How It Works

The application operates on CrewAI's `hierarchical` process, where a **Coordinator Agent** acts as the mission manager.

1.  **Mission Start:** The user provides a target (domain or IP) via the Streamlit UI.
2.  **Task Delegation:** The Coordinator assigns the **Reconnaissance** task to the specialist agent.
3.  **Execution & Logging:** The Recon Agent executes its toolchain (`Nmap`, `GoBuster`, web searches) and meticulously logs the full, raw output of every action to an intermediate report file (`recon_report.md`).
4.  **Handoff:** The Coordinator passes the context to the **Exploitation Agent**, which reads the recon report, researches exploits, and attempts to gain initial access, logging its actions to `exploit_report.md`.
5.  **Escalation:** The **Post-Exploitation Agent** takes over, attempting to escalate privileges and logging its findings to `privesc_report.md`.
6.  **Final Synthesis:** The Coordinator Agent's final task is to read all intermediate reports and compile them into a single, detailed, and chronologically-ordered final attack narrative.

---

## ⚠️ Disclaimer

This tool is for **educational and authorized security testing purposes ONLY**. Running these tools against systems you do not own is illegal. The developer is not responsible for any misuse or damage caused by this program. Always obtain explicit, written permission from the system owner before conducting any security testing.

---

## 🚀 Setup Option 1: Manual Installation

Follow these steps to get the AI Red Team Crew up and running on your local machine.

### 1. Prerequisites: System Tools

The AI agents control real command-line tools. You **must** have them installed on your system.

**For Debian/Ubuntu-based systems (like Kali Linux, Ubuntu):**
```bash
sudo apt update
sudo apt install nmap gobuster sqlmap hydra whois -y
```

### 2. Setup: Python Environment & Dependencies

It is highly recommended to use a Python virtual environment.

```bash
# 1. Clone the repository
git clone https://github.com/patelankit706/redteamagent.git
cd redteamagent

# 2. Create and activate a virtual environment using uv
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12
source .venv/bin/activate

# 3. Install the required Python packages
uv pip install -r requirements.txt
```

### 3. Configuration: API Keys

The application requires API keys for the LLM (Cerebras) and the web search tool (Serper).

 Get your API keys from following url:

```env
# Get your cerebras key from https://www.cerebras.ai/

# Get your key from https://serper.dev/
```

### 4. Running the Application

Once the prerequisites are installed and your API keys are configured, launch the Streamlit app with a single command:

```bash
streamlit run app.py
```
Navigate to the local URL provided by Streamlit in your browser, configure your target, cerebras and serper api keys in the sidebar and launch the crew!

---

## 🚀 Setup Option 2: Running with Docker prebuilt image (Recommended)

This is the easiest way to run the application, as it handles all system and Python dependencies automatically.

### Prerequisites
- [Docker](https://www.docker.com/get-started) must be installed and running on your system.


### Run the Docker Container
```bash
docker run --rm -p 8501:8501 patelankit706/ml_ai_sec:latest
```
Navigate to the local URL provided by Streamlit in your browser, configure your target, cerebras and serper api keys in the sidebar and launch the crew!

---

## 📁 Project Structure

```
/ai-red-team-crew/
├── app.py                  # Main Streamlit application
├── agents.py               # All CrewAI Agent definitions
├── tasks.py                # All CrewAI Task definitions
├── README.md               
├── requirements.txt        # Python dependencies
└── tools/
    ├── __init__.py
    ├── domain_tools.py
    ├── exploitation_tools.py
    ├── file_tools.py
    ├── post_exploitation_tools.py
    └── recon_tools.py
```

---

## 🗺️ Roadmap & Future Improvements

This project is a basic functional prototype with many avenues for expansion:

*   [ ] **Add More Tools:** Integrate more tools for different phases (e.g., password cracking, vulnerability scanning).
*   [ ] **Persistence Agent:** Create a new agent responsible for establishing persistence on the target.
*   [ ] **Windows Target Support:** Develop tools and agent prompts specifically for Windows environments.
*   [ ] **C2 Framework Integration:** Connect the agents to a simple Command & Control framework for more complex post-exploitation.
*   [ ] **User-Selectable Models:** Allow users to choose different LLMs (OpenAI, Anthropic, local models) via the UI.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, tools, or improvements, please feel free to open an issue or submit a pull request.

## 📜 License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.
