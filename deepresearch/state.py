from typing import Dict, List, Optional, TypedDict

class SummaryState(TypedDict, total=False):
    """State for the summary graph."""
    research_topic: str
    search_query: str
    running_summary: str
    research_loop_count: int
    web_research_results: List[str]
    sources_gathered: List[str]
    linkedin_profiles: List[Dict[str, str]]

class SummaryStateInput(TypedDict):
    """Input state for the summary graph."""
    research_topic: str

class SummaryStateOutput(TypedDict):
    """Output state for the summary graph."""
    research_topic: str
    running_summary: str