import argparse
import os
import threading
import sys
from dotenv import load_dotenv

from deepresearch.graph import graph
from deepresearch.linkedin_service import start_service

def main():
    """Main entry point for running the lead generation agent."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Lead Generation Agent with LinkedIn Access")
    parser.add_argument("lead_criteria", type=str, nargs="?", help="Criteria for lead generation (e.g., 'startup CTOs in fintech')")
    parser.add_argument("--linkedin-service", action="store_true", help="Start the LinkedIn service")
    parser.add_argument("--port", type=int, default=8080, help="Port for the LinkedIn service")
    parser.add_argument("--max-loops", type=int, default=3, help="Maximum number of research loops")
    
    args = parser.parse_args()
    
    # Start LinkedIn service if requested
    if args.linkedin_service:
        print(f"Starting LinkedIn service on port {args.port}...")
        service_thread = threading.Thread(target=start_service, args=(args.port,))
        service_thread.daemon = True
        service_thread.start()
        print(f"LinkedIn service is running at http://localhost:{args.port}")
        print("Use Ctrl+C to stop the service.")
        
        try:
            # Keep the main thread alive
            service_thread.join()
        except KeyboardInterrupt:
            print("\nShutting down LinkedIn service...")
            sys.exit(0)
    
    # Run the lead generation agent if criteria are provided
    if args.lead_criteria:
        print(f"Starting lead generation for: {args.lead_criteria}")
        print(f"Maximum search loops: {args.max_loops}")
        
        # Run the graph
        result = graph.invoke(
            {"research_topic": args.lead_criteria},
            {"configurable": {"max_web_research_loops": args.max_loops}}
        )
        
        # Print the result
        print("\n" + "="*50)
        print("LEAD GENERATION RESULTS:")
        print("="*50)
        print(result["running_summary"])
        print("="*50)
    elif not args.linkedin_service:
        parser.print_help()

if __name__ == "__main__":
    main()