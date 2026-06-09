
import os
import subprocess
from crewai.tools import BaseTool

class NmapScanTool(BaseTool):
    name: str = "Nmap Port Scanner"
    description: str = "Utilizes Nmap to scan a target IP address for open ports and running services. Input should be a valid IP address."

    def _run(self, ip_address: str) -> str:
        print(f"--- Running Nmap scan on {ip_address} ---")
        try:
            # Using -sV for version detection, -T4 for faster execution, and scanning top 1000 ports
            command = ["nmap", "-sV", "-T4", ip_address]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"--- Nmap scan completed for {ip_address} ---")
            return f"Nmap scan results for {ip_address}:\n{result.stdout}"
        except FileNotFoundError:
            return "Error: nmap is not installed or not in PATH. Please install nmap."
        except subprocess.CalledProcessError as e:
            return f"Error during nmap scan on {ip_address}: {e.stderr}"

class GoBusterTool(BaseTool):
    name: str = "GoBuster Directory and File Brute-forcer"
    description: str = "Uses GoBuster to find hidden directories and files on a web server. Input should be a target URL."

    def _run(self, url: str) -> str:
        # A common wordlist, ensure this path is correct or provide a way to configure it.
        # This is a common path in Kali Linux.
        wordlist = "directory-list-2.3-medium.txt"
        if not os.path.exists(wordlist):
            return f"Error: Wordlist not found at {wordlist}. Please specify the correct path."
        
        print(f"--- Running GoBuster on {url} ---")
        try:
            command = ["gobuster", "dir", "-u", url, "-w", wordlist, "-q", "-t", "50"] # -q for quiet, -t for threads
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            print(f"--- GoBuster scan completed for {url} ---")
            return f"GoBuster results for {url}:\n{result.stdout}"
        except FileNotFoundError:
            return "Error: gobuster is not installed or not in PATH. Please install gobuster."
        except subprocess.CalledProcessError as e:
            return f"Error during GoBuster scan on {url}: {e.stderr}"