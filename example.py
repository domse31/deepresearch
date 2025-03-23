#!/usr/bin/env python3
"""
Example script showing how to use the Lead Generation Agent with LinkedIn access.
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

def generate_leads(criteria, max_loops=3):
    """Run the lead generation agent with specific criteria."""
    print(f"Generating leads for: {criteria}")
    result = subprocess.run(
        ["python", "-m", "deepresearch.run", criteria, "--max-loops", str(max_loops)],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)

def main():
    """Main function to demonstrate using the lead generation agent."""
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
        
        # Example lead criteria
        print("\nExample lead criteria:")
        print("1. VP of Engineering at Series B startups in healthcare")
        print("2. Marketing Directors at Fortune 500 companies")
        print("3. Founders of AI startups in Europe")
        print("4. Product Managers with fintech experience in New York")
        
        # Ask user for input
        criteria = input("\nEnter lead criteria: ")
        max_loops = input("Enter maximum search loops (default 3): ")
        
        if not max_loops:
            max_loops = 3
        else:
            max_loops = int(max_loops)
        
        if criteria:
            generate_leads(criteria, max_loops)
    
    finally:
        # Clean up
        print("\nStopping LinkedIn service...")
        linkedin_process.terminate()
        linkedin_process.wait()
        print("LinkedIn service stopped")

if __name__ == "__main__":
    main()