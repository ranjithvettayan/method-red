import os
from crewai.tools import BaseTool

class FileWriteTool(BaseTool):
    name: str = "File Write Tool"
    description: str = ("Writes content to a specified file. "
                        "Input should be a string with the file path and content separated by a pipe '|'. "
                        "Example: 'path/to/my_report.md|This is the content of the file.'")

    def _run(self, data: str) -> str:
        try:
            path, content = data.split('|', 1)
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'a') as f:
                f.write("\n\n\n"+content)
            return f"Successfully wrote {len(content)} characters to {path}."
        except Exception as e:
            return f"Error writing to file: {e}"