#!/usr/bin/env python3
"""
Entry point for Red Team MCP
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from src.main import main

if __name__ == "__main__":
    main()
