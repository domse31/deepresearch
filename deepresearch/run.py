import argparse
import os
import threading
import sys
from dotenv import load_dotenv

from deepresearch.graph import graph
from deepresearch.linkedin_service import start_service

def main():
    """Main entry point for running the deep research agent."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Deep Research Agent with LinkedIn Access")
    parser.add_argument("research_topic", type=str, nargs="?", help="Topic to research")
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
    
    # Run the research agent if a topic is provided
    if args.research_topic:
        print(f"Starting research on: {args.research_topic}")
        print(f"Maximum research loops: {args.max_loops}")
        
        # Run the graph
        result = graph.invoke(
            {"research_topic": args.research_topic},
            {"configurable": {"max_web_research_loops": args.max_loops}}
        )
        
        # Print the result
        print("\n" + "="*50)
        print("RESEARCH RESULTS:")
        print("="*50)
        print(result["running_summary"])
        print("="*50)
    elif not args.linkedin_service:
        parser.print_help()

if __name__ == "__main__":
    main()