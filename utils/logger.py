# Logging setup
import os
import logging
from datetime import datetime

def setup_logging_directory():
    # Create logs directory if it doesn't exist
    logs_dir = "response_logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    return logs_dir


def log_response(log_dir, response, query, model, response_text, run_id, attempt_id):
    """Log an LLM response to a txt file"""
    
    filename = f"{log_dir}/run_{run_id}.txt"

    with open(filename, "a") as f:
        f.write(f"Query: {query}\n")
        f.write(f"Response: {response_text}\n")
        f.write(f"Model: {model}\n")
        f.write(f"Run ID: {run_id}\n")
        f.write(f"Attempt ID: {attempt_id}\n")
        f.write(f"Response: {response}\n")

    return filename