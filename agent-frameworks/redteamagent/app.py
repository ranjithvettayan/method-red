import streamlit as st
import os
import re
from dotenv import load_dotenv
from crewai import Crew, Process
from crewai import LLM
import logging
from contextlib import redirect_stdout
from io import StringIO
from datetime import datetime

from agents import RedTeamAgents
from tasks import RedTeamTasks

# Load environment variables from .env file
load_dotenv()

# --- Real-time Log Streaming Handler ---
class StreamlitLogHandler(StringIO):
    def __init__(self, placeholder):
        super().__init__()
        self.placeholder = placeholder
        self.buffer = ""
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    def write(self, s):
        s = self.ansi_escape.sub('', s)
        self.buffer += s
        self.placeholder.code(self.buffer, language='log')

    def flush(self):
        pass

# --- Streamlit GUI ---
st.set_page_config(page_title="AI Red Team Crew", layout="wide")

st.title("🤖 AI Red Team Crew (Llama 3.3 Edition)")
st.markdown("""
This application uses a crew of AI agents to simulate a cybersecurity red team engagement.
Enter a target below and launch the crew to begin the assessment.
**Disclaimer:** This is for educational and authorized purposes only.
""")

# Sidebar for inputs
with st.sidebar:
    st.header("🎯 Target Configuration")
    target = st.text_input("Target Domain or IP Address", "example.com")
    
    st.markdown("---")
    st.header("🔑 API Keys")
    cerebras_api_key = st.text_input("Cerebras API Key", type="password", value=os.getenv("CEREBRAS_API_KEY") or "")
    serper_api_key = st.text_input("Serper API Key", type="password", value=os.getenv("SERPER_API_KEY") or "")
    
    st.markdown("---")
    launch_button = st.button("🚀 Launch Red Team Crew")

# --- Main content area Layout ---

# Section for the Final Report
st.header("Final Report")
report_container = st.container(border=True)
report_placeholder = report_container.empty()
report_placeholder.info("The final report will be displayed here upon mission completion.")

# Section for Live Logs with dynamic header
log_header_cols = st.columns([0.85, 0.15]) # Create columns for title and spinner
log_header_cols[0].header("Agent & Tool Logs")
log_spinner_placeholder = log_header_cols[1].empty() # Placeholder for the spinner

log_container = st.container(height=400)
log_content_placeholder = log_container.empty()
log_content_placeholder.info("Logs will appear here once the mission starts...")


# Main execution logic
if launch_button:
    if not target:
        st.error("Please provide a Target Domain or IP Address.")
    elif not cerebras_api_key or not serper_api_key:
        st.error("Please provide both Cerebras and Serper API keys.")
    else:
        
        # Set environment variables
        os.environ["CEREBRAS_API_KEY"] = cerebras_api_key
        os.environ["SERPER_API_KEY"] = serper_api_key
        
        # Create a unique mission directory for report files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_target_name = re.sub(r'[^a-zA-Z0-9]', '_', target)
        mission_dir = f"mission_reports/{timestamp}_{safe_target_name}"
        os.makedirs(mission_dir, exist_ok=True)
        
        # --- ACTIVATE DYNAMIC UI ELEMENTS ---
        log_spinner_placeholder.info("⏳")
        report_placeholder.info("Final report being prepared by Coordinator Agent... ⏳")
        log_content_placeholder.info(f"🚀 Mission started for target: {target}. . Intermediate reports will be saved in '{mission_dir}'")
        

        log_handler = StreamlitLogHandler(log_content_placeholder)

        try:
            llm = LLM(
                    model="cerebras/llama3.3-70b", # Replace with your chosen Cerebras model name, e.g., "cerebras/llama3.1-8b"
                    api_key=os.environ.get("CEREBRAS_API_KEY"), # Your Cerebras API key
                    base_url="https://api.cerebras.ai/v1",
                    temperature=0.5,
                    # Optional parameters:
                    # top_p=1,
                    # max_completion_tokens=8192, # Max tokens for the response
                    # response_format={"type": "json_object"} # Ensures the response is in JSON format
                )

            agents = RedTeamAgents()
            tasks = RedTeamTasks()

            # Instantiate agents and tasks
            coordinator = agents.red_team_coordinator(llm=llm)
            recon_specialist = agents.reconnaissance_specialist(llm=llm)
            exploit_specialist = agents.exploitation_specialist(llm=llm)
            privesc_specialist = agents.post_exploitation_specialist(llm=llm)

            recon = tasks.recon_task(recon_specialist, target, mission_dir)
            exploit = tasks.exploit_task(exploit_specialist, recon, mission_dir)
            privesc = tasks.privesc_task(privesc_specialist, exploit, mission_dir)
            reporting = tasks.reporting_task(coordinator, [recon, exploit, privesc], mission_dir)
            
            crew = Crew(
                agents=[coordinator, recon_specialist, exploit_specialist, privesc_specialist],
                tasks=[recon, exploit, privesc, reporting],
                process=Process.hierarchical,
                manager_llm=llm,
                verbose=True
            )

            # Kick off the crew's work, streaming logs to the UI
            final_report = ""
            with redirect_stdout(log_handler):
                print("--- Assembling Crew with Llama 3.3 and Beginning Mission ---")
                final_report = crew.kickoff()
                print("\n--- Mission Complete ---")

            # --- UPDATE UI UPON SUCCESS ---
            log_spinner_placeholder.success("Done!")
            report_placeholder.empty() # Clear the spinner
            with report_container:
                st.success("✅ Mission Completed!")
                with st.expander("View Detailed Attack Narrative", expanded=True):
                    st.markdown(final_report)

        except Exception as e:
            # --- UPDATE UI UPON FAILURE ---
            log_spinner_placeholder.error("Failed!")
            report_placeholder.error("Report generation failed due to a mission error.")
            st.error(f"An error occurred during the mission: {e}")
            logging.error(f"Mission failed with an exception: {e}", exc_info=True)