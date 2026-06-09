# Use a stable Python 3.11 base image based on Debian
FROM python:3.11-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Prevent apt-get from asking for user input
ENV DEBIAN_FRONTEND=noninteractive

# Update the package list and install all system-level dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nmap \
    gobuster \
    sqlmap \
    hydra \
    whois \
    git \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# --- SECURITY AND PERMISSIONS FIX ---
# Create a non-root user 'appuser' with a dedicated home directory at /home/appuser
RUN useradd -m -s /bin/bash appuser
# Explicitly set the HOME environment variable for all subsequent commands
ENV HOME=/home/appuser
# --- END FIX ---

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
# --no-cache-dir is used to keep the image size smaller
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# --- PERMISSIONS FIX CONTINUED ---
# Change the ownership of the app directory and all its contents to our new user.
# This is crucial so the app can create the 'mission_reports' directory.
RUN chown -R appuser:appuser /app

# Switch from the root user to our new unprivileged user
USER appuser
# --- END FIX ---

# Expose the port that Streamlit runs on
EXPOSE 8501

# Define the healthcheck to ensure the app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# The command to run your Streamlit application
# This command will now be executed by 'appuser'
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
