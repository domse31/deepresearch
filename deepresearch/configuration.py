import os
from typing import Optional, Literal
from pydantic import BaseModel, Field

# Define a simple enum for search API
SearchAPI = Literal["tavily"]

class Configuration(BaseModel):
    """Configuration for the deep research agent.
    
    Simplified to use only OpenAI and one search API.
    """
    openai_api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("OPENAI_API_KEY"))
    llm_model: str = Field(default="gpt-3.5-turbo-16k")
    search_api: SearchAPI = Field(default="tavily")
    tavily_api_key: Optional[str] = Field(default_factory=lambda: os.environ.get("TAVILY_API_KEY"))
    max_web_research_loops: int = Field(default=3)
    clay_webhook_url: Optional[str] = Field(
        default_factory=lambda: os.environ.get("CLAY_WEBHOOK_URL")
    )
    
    @classmethod
    def from_runnable_config(cls, config):
        """Create a configuration from a runnable config."""
        if hasattr(config, "configurable"):
            return config.configurable
        return Configuration()