
import socket
import subprocess
from crewai.tools import BaseTool

class ResolveDomainTool(BaseTool):
    name: str = "Resolve Domain to IP"
    description: str = "Resolves a given domain name to its IPv4 address. Input must be a valid domain name."

    def _run(self, domain: str) -> str:
        print(f"--- Resolving domain: {domain} ---")
        try:
            ip_address = socket.gethostbyname(domain)
            return f"The IP address for {domain} is {ip_address}"
        except socket.gaierror as e:
            return f"Error: Could not resolve domain '{domain}'. It may be invalid or unreachable. Details: {e}"

class WhoisTool(BaseTool):
    name: str = "Whois Lookup Tool"
    description: str = "Performs a WHOIS lookup for a given domain to find registration and contact information. Input must be a valid domain name."

    def _run(self, domain: str) -> str:
        print(f"--- Performing WHOIS lookup for {domain} ---")
        try:
            command = ["whois", domain]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return f"WHOIS information for {domain}:\n{result.stdout}"
        except FileNotFoundError:
            return "Error: 'whois' command not found. Please install it on your system."
        except subprocess.CalledProcessError as e:
            return f"Error during WHOIS lookup for {domain}: {e.stderr}"