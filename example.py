#!/usr/bin/env python3
"""
Example script showing how to use the Deep Research Agent with LinkedIn access.
"""

from dotenv import load_dotenv
import subprocess
import threading
import time
import os

# Load environment variables
load_dotenv()

def start_linkedin_service():
    """Start the LinkedIn service in a separate process."""
    print("Starting LinkedIn service...")
    linkedin_process = subprocess.Popen(
        ["python", "-m", "deepresearch.run", "--linkedin-service"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return linkedin_process

def research_topic(topic, max_loops=3):
    """Run the research agent on a topic."""
    print(f"Researching topic: {topic}")
    result = subprocess.run(
        ["python", "-m", "deepresearch.run", topic, "--max-loops", str(max_loops)],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

def main():
    """Main function to demonstrate using the agent."""
    # Start the LinkedIn service
    linkedin_process = start_linkedin_service()
    
    # Wait for the service to start
    time.sleep(2)
    print("LinkedIn service is now running")
    
    try:
        # Instructions for ngrok
        print("\nIMPORTANT: In another terminal, start ngrok with:")
        print("  ngrok http 8080")
        print("\nThen update your .env file with the ngrok URL")
        
        # Example research topics with LinkedIn profiles
        print("\nResearch examples:")
        print("1. Research topic with LinkedIn: Tech leadership at OpenAI")
        print("2. Research topic with LinkedIn: Prominent AI researchers at Google")
        
        # Ask user for input
        topic = input("\nEnter a research topic: ")
        max_loops = input("Enter maximum research loops (default 3): ")
        
        if not max_loops:
            max_loops = 3
        else:
            max_loops = int(max_loops)
        
        if topic:
            research_topic(topic, max_loops)
    
    finally:
        # Clean up
        print("\nStopping LinkedIn service...")
        linkedin_process.terminate()
        linkedin_process.wait()
        print("LinkedIn service stopped")

if __name__ == "__main__":
    main()