import json
import os
from typing_extensions import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import add_messages
from langsmith import Client

from deepresearch.configuration import Configuration
from deepresearch.utils import (
    tavily_search, 
    format_sources, 
    deduplicate_and_format_sources, 
    extract_linkedin_urls,
    get_linkedin_profile_data
)
from deepresearch.state import SummaryState, SummaryStateInput, SummaryStateOutput
from deepresearch.prompts import (
    query_writer_instructions, 
    summarizer_instructions, 
    reflection_instructions, 
    get_current_date
)

# Initialize LangSmith if environment variables are set
if os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT"):
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGSMITH_TRACING", "false").lower()
    if os.getenv("LANGSMITH_ENDPOINT"):
        os.environ["LANGCHAIN_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
    
    # Initialize LangSmith client
    langsmith_client = Client(
        api_key=os.getenv("LANGSMITH_API_KEY"),
        api_url=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    )
    
    # Set project name
    if os.getenv("LANGSMITH_PROJECT"):
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

# Nodes
def generate_query(state, config: RunnableConfig):
    """LangGraph node that generates a search query based on the research topic.
    
    Uses OpenAI to create an optimized search query for web research based on
    the user's research topic.
    
    Args:
        state: Current graph state containing the research topic
        config: Configuration for the runnable, including model settings
        
    Returns:
        Dictionary with state update, including search_query key containing the generated query
    """

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=state["research_topic"]
    )

    # Generate a query
    configurable = Configuration.from_runnable_config(config)
    
    llm_json_mode = ChatOpenAI(
        model=configurable.llm_model,
        api_key=configurable.openai_api_key,
        response_format={"type": "json_object"}
    )
    
    result = llm_json_mode.invoke(
        [SystemMessage(content=formatted_prompt),
        HumanMessage(content=f"Generate a query for web search:")]
    )
    
    # Get the content
    content = result.content

    # Parse the JSON response and get the query
    try:
        query = json.loads(content)
        search_query = query['query']
    except (json.JSONDecodeError, KeyError):
        # If parsing fails or the key is not found, use a fallback query
        search_query = content
    return {"search_query": search_query}

def web_research(state, config: RunnableConfig):
    """LangGraph node that performs web research using the generated search query.
    
    Executes a web search using Tavily and formats the results for further processing.
    Also extracts and processes any LinkedIn profile URLs found in the results.
    
    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings
        
    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count,
        web_research_results, and linkedin_profiles
    """

    # Configure
    configurable = Configuration.from_runnable_config(config)
    
    # Ensure we have a search query
    search_query = state.get("search_query", "")
    if not search_query:
        search_query = f"research about {state.get('research_topic', 'AI research')}"
    
    # Get current research loop count with default
    research_loop_count = state.get("research_loop_count", 0)
    
    # Get current LinkedIn profiles with default
    linkedin_profiles = state.get("linkedin_profiles", [])

    # Search the web
    search_results = tavily_search(search_query, max_results=5)
    search_str = deduplicate_and_format_sources(search_results, max_tokens_per_source=1000)
    
    # Process LinkedIn URLs from the search results
    linkedin_urls = []
    for result in search_results:
        # Extract LinkedIn URLs from result content and URL
        content_urls = extract_linkedin_urls(result.get("content", ""))
        title_urls = extract_linkedin_urls(result.get("title", ""))
        linkedin_urls.extend(content_urls + title_urls)
    
    # Deduplicate LinkedIn URLs
    linkedin_urls = list(set(linkedin_urls))
    
    # Process LinkedIn profiles if any found
    new_linkedin_profiles = []
    for url in linkedin_urls:
        profile_data = get_linkedin_profile_data(url)
        new_linkedin_profiles.append(profile_data)
    
    # Update LinkedIn profiles list
    linkedin_profiles.extend(new_linkedin_profiles)
    
    return {
        "sources_gathered": [format_sources(search_results)], 
        "research_loop_count": research_loop_count + 1, 
        "web_research_results": [search_str],
        "linkedin_profiles": linkedin_profiles
    }

def summarize_sources(state, config: RunnableConfig):
    """LangGraph node that summarizes web research results.
    
    Uses an LLM to create or update a running summary based on the newest web research 
    results, integrating them with any existing summary. Also includes LinkedIn profile
    information when available.
    
    Args:
        state: Current graph state containing research topic, running summary,
              web research results, and linkedin_profiles
        config: Configuration for the runnable, including LLM provider settings
        
    Returns:
        Dictionary with state update, including running_summary key containing the updated summary
    """

    # Existing summary with default
    existing_summary = state.get("running_summary", "")

    # Get research topic with default
    research_topic = state.get("research_topic", "AI research")

    # Most recent web research with default
    web_research_results = state.get("web_research_results", [])
    if not web_research_results:
        web_research_results = ["No web research results available yet."]
    most_recent_web_research = web_research_results[-1]
    
    # Get LinkedIn profiles with default
    linkedin_profiles = state.get("linkedin_profiles", [])
    
    # Format LinkedIn profiles for inclusion in the summary
    linkedin_info = ""
    if linkedin_profiles:
        linkedin_info = "\n\n<LinkedIn Profiles>\n"
        for profile in linkedin_profiles:
            url = profile.get("url", "No URL")
            name = profile.get("name", "Unknown")
            title = profile.get("title", "No title")
            company = profile.get("company", "No company")
            status = profile.get("status", "complete")
            
            linkedin_info += f"- {name}: {title} at {company} | {url}"
            if status == "pending":
                linkedin_info += " (Profile data requested and will be available in future runs)"
            linkedin_info += "\n"
        linkedin_info += "</LinkedIn Profiles>"

    # Build the human message
    if existing_summary:
        human_message_content = (
            f"<User Input> \n {research_topic} \n </User Input>\n\n"
            f"<Existing Summary> \n {existing_summary} \n </Existing Summary>\n\n"
            f"<New Search Results> \n {most_recent_web_research} \n </New Search Results>"
        )
        if linkedin_info:
            human_message_content += f"\n\n{linkedin_info}"
    else:
        human_message_content = (
            f"<User Input> \n {research_topic} \n </User Input>\n\n"
            f"<Search Results> \n {most_recent_web_research} \n </Search Results>"
        )
        if linkedin_info:
            human_message_content += f"\n\n{linkedin_info}"

    # Run the LLM
    configurable = Configuration.from_runnable_config(config)
    
    llm = ChatOpenAI(
        model=configurable.llm_model,
        api_key=configurable.openai_api_key
    )
    
    result = llm.invoke(
        [SystemMessage(content=summarizer_instructions),
        HumanMessage(content=human_message_content)]
    )

    running_summary = result.content

    return {"running_summary": running_summary}

def reflect_on_summary(state, config: RunnableConfig):
    """LangGraph node that identifies knowledge gaps and generates follow-up queries.
    
    Analyzes the current summary to identify areas for further research and generates
    a new search query to address those gaps. Uses structured output to extract
    the follow-up query in JSON format.
    
    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings
        
    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """

    # Get state values with defaults
    research_topic = state.get("research_topic", "AI research")
    running_summary = state.get("running_summary", "No summary available yet.")

    # Generate a query
    configurable = Configuration.from_runnable_config(config)
    
    llm_json_mode = ChatOpenAI(
        model=configurable.llm_model,
        api_key=configurable.openai_api_key,
        response_format={"type": "json_object"}
    )
    
    result = llm_json_mode.invoke(
        [SystemMessage(content=reflection_instructions.format(research_topic=research_topic)),
        HumanMessage(content=f"Reflect on our existing knowledge: \n === \n {running_summary}, \n === \n And now identify a knowledge gap and generate a follow-up web search query:")]
    )
    
    # Get the content
    content = result.content
    
    # Parse the JSON response and get the query
    try:
        query = json.loads(content)
        search_query = query['query']
    except (json.JSONDecodeError, KeyError):
        # If parsing fails or the key is not found, use the raw content
        search_query = content
    
    return {"search_query": search_query}

def finalize_summary(state):
    """LangGraph node that finalizes the research summary.
    
    Prepares the final output by formatting the running summary with LinkedIn profiles
    and other sources for a comprehensive research report.
    
    Args:
        state: Current graph state containing the running summary, sources gathered, and linkedin_profiles
        
    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary
    """

    # Get values with defaults
    running_summary = state.get("running_summary", "No summary available.")
    sources_gathered = state.get("sources_gathered", [])
    linkedin_profiles = state.get("linkedin_profiles", [])

    # Deduplicate sources before joining
    seen_sources = set()
    unique_sources = []
    
    for source in sources_gathered:
        # Split the source into lines and process each individually
        for line in source.split('\n'):
            # Only process non-empty lines
            if line.strip() and line not in seen_sources:
                seen_sources.add(line)
                unique_sources.append(line)
    
    # Create LinkedIn profiles section if profiles were found
    linkedin_section = ""
    if linkedin_profiles:
        linkedin_section = "\n\n## LinkedIn Profiles\n"
        for profile in linkedin_profiles:
            url = profile.get("url", "No URL")
            name = profile.get("name", "Unknown")
            title = profile.get("title", "No title")
            company = profile.get("company", "No company")
            
            linkedin_section += f"- {name}: {title} at {company} | {url}\n"
    
    # Join the deduplicated sources
    all_sources = "\n".join(unique_sources)
    
    final_summary = f"## Summary\n\n{running_summary}\n\n### Sources:\n{all_sources}"
    
    if linkedin_section:
        final_summary += linkedin_section
        
    return {"running_summary": final_summary}

def route_research(state, config: RunnableConfig) -> Literal["finalize_summary", "web_research"]:
    """LangGraph routing function that determines the next step in the research flow.
    
    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.
    
    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_web_research_loops setting
        
    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """

    configurable = Configuration.from_runnable_config(config)
    research_loop_count = state.get("research_loop_count", 0)
    if research_loop_count <= configurable.max_web_research_loops:
        return "web_research"
    else:
        return "finalize_summary"

# Add nodes and edges
builder = StateGraph(SummaryState, input=SummaryStateInput, output=SummaryStateOutput, config_schema=Configuration)
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("summarize_sources", summarize_sources)
builder.add_node("reflect_on_summary", reflect_on_summary)
builder.add_node("finalize_summary", finalize_summary)

# Add edges
builder.add_edge(START, "generate_query")
builder.add_edge("generate_query", "web_research")
builder.add_edge("web_research", "summarize_sources")
builder.add_edge("summarize_sources", "reflect_on_summary")
builder.add_conditional_edges("reflect_on_summary", route_research)
builder.add_edge("finalize_summary", END)

graph = builder.compile()

# Add this to register the graph with a workspace
if __name__ == "__main__":
    try:
        from langgraph.app import server
        
        # Register the graph with a name
        server.add_graph("deep_researcher", graph)
        
        # Enable LangSmith tracing if environment variables are configured
        if os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT"):
            print(f"LangSmith tracing enabled for project: {os.getenv('LANGSMITH_PROJECT')}")
        else:
            print("LangSmith tracing not configured. Set LANGSMITH_API_KEY and LANGSMITH_PROJECT to enable.")
        
        # Start the server
        server.serve(port=8123)
    except ImportError:
        try:
            from langgraph.cli.run import run_graph
            
            # Enable LangSmith tracing if environment variables are configured
            if os.getenv("LANGSMITH_API_KEY") and os.getenv("LANGSMITH_PROJECT"):
                print(f"LangSmith tracing enabled for project: {os.getenv('LANGSMITH_PROJECT')}")
            else:
                print("LangSmith tracing not configured. Set LANGSMITH_API_KEY and LANGSMITH_PROJECT to enable.")
            
            # Run the graph directly
            run_graph(graph, "deep_researcher", port=8123)
        except ImportError:
            print("Error: Could not find langgraph.app.server or langgraph.cli.run")
            print("Please check your langgraph version or try running: langgraph run")