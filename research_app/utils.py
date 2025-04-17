# Utility functions for the research application

import logging
import json
import os
import time
from datetime import datetime

# Set up logging
def setup_logging(log_level=logging.INFO):
    """
    Configure logging for the application
    """
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)

# Function to ensure directories exist
def ensure_directories(directories):
    """
    Create directories if they don't exist
    """
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

# Function to save research results
def save_research_results(query, report, citations, output_dir="/app/data/reports"):
    """
    Save research results to JSON file
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a safe filename from query
    safe_query = "".join(c if c.isalnum() else "_" for c in query)[:50]
    filename = f"{output_dir}/{timestamp}_{safe_query}.json"

    # Prepare the data
    data = {
        "query": query,
        "timestamp": timestamp,
        "report": report,
        "citations": citations
    }

    # Save to file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return filename

# Function to format citations
def format_citations(citations):
    """
    Format citations for display
    """
    formatted_citations = []

    for citation in citations:
        cid = citation.get("id", "")
        title = citation.get("title", "Untitled")
        url = citation.get("url", "")
        retrieval_date = citation.get("retrieval_date", "")

        formatted = f"[{cid}] {title}"
        if url:
            formatted += f", URL: {url}"
        if retrieval_date:
            formatted += f", Retrieved on: {retrieval_date}"

        formatted_citations.append(formatted)

    return formatted_citations

# Performance monitoring
def timing_decorator(func):
    """
    Decorator to measure and log function execution time
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"Function {func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper
