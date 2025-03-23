import os
import re
import json
import requests
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Directory to store received LinkedIn profiles
PROFILES_DIR = "linkedin_profiles"
os.makedirs(PROFILES_DIR, exist_ok=True)

def tavily_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the web using Tavily API.
    
    Args:
        query: The search query
        max_results: Maximum number of results to return
        
    Returns:
        List of search results as dictionaries with title, content, and url
    """
    import os
    import requests
    
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("Tavily API key not found. Please set the TAVILY_API_KEY environment variable.")
    
    search_url = "https://api.tavily.com/search"
    params = {
        "api_key": api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": False,
        "include_images": False,
        "max_results": max_results
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        raise Exception(f"Tavily search failed with status code {response.status_code}: {response.text}")
    
    results = response.json().get("results", [])
    search_results = []
    
    for result in results:
        search_results.append({
            "title": result.get("title", ""),
            "content": result.get("content", ""),
            "url": result.get("url", "")
        })
    
    return search_results

def format_sources(sources: List[Dict[str, str]]) -> str:
    """Format the sources for output.
    
    Args:
        sources: List of sources with title, content, and url
        
    Returns:
        Formatted string with sources
    """
    formatted_sources = []
    for i, source in enumerate(sources, 1):
        formatted_sources.append(f"{i}. {source['title']} - {source['url']}")
    return "\n".join(formatted_sources)

def deduplicate_and_format_sources(sources: List[Dict[str, str]], 
                                  max_tokens_per_source: int = 1000) -> str:
    """Deduplicate sources and format them for the model.
    
    Args:
        sources: List of sources with title, content, and url
        max_tokens_per_source: Maximum tokens per source to include
        
    Returns:
        Formatted string with sources content
    """
    seen_urls = set()
    unique_sources = []
    
    for source in sources:
        url = source.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(source)
    
    formatted_sources = []
    for i, source in enumerate(unique_sources, 1):
        title = source.get("title", "")
        content = source.get("content", "")
        url = source.get("url", "")
        
        # Truncate content if needed based on rough token estimate
        if content and len(content) > max_tokens_per_source * 4:  # Rough char to token ratio
            content = content[:max_tokens_per_source * 4] + "..."
        
        formatted_source = f"SOURCE {i}:\nTitle: {title}\nURL: {url}\nContent: {content}\n"
        formatted_sources.append(formatted_source)
    
    return "\n\n".join(formatted_sources)

def extract_linkedin_urls(text: str) -> List[str]:
    """
    Extract LinkedIn profile URLs from text.
    
    Args:
        text: Text to extract URLs from
        
    Returns:
        List of LinkedIn profile URLs
    """
    # Pattern to match LinkedIn profile URLs
    linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
    return re.findall(linkedin_pattern, text)

def send_linkedin_profile_to_clay(profile_url: str) -> Dict[str, Any]:
    """
    Send a LinkedIn profile URL to Clay for enrichment.
    
    Args:
        profile_url: LinkedIn profile URL
        
    Returns:
        Response from Clay API
    """
    clay_webhook_url = os.environ.get("CLAY_WEBHOOK_URL")
    if not clay_webhook_url:
        raise ValueError("Clay webhook URL not found. Please set the CLAY_WEBHOOK_URL environment variable.")
    
    try:
        # Get webhook callback URL (this would be set up with ngrok in production)
        callback_url = os.environ.get("CALLBACK_URL", "http://localhost:8080/webhook/clay-callback")
        
        # Send the profile URL to Clay
        response = requests.post(
            clay_webhook_url,
            json={
                "url": profile_url,
                "callback_url": callback_url
            }
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent LinkedIn profile to Clay: {profile_url}")
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"status": "success", "message": "Request accepted by Clay"}
        else:
            logger.warning(f"Failed to send LinkedIn profile to Clay: {profile_url}. Status: {response.status_code}")
            return {"error": f"Request failed with status code: {response.status_code}"}
            
    except Exception as e:
        logger.error(f"Error sending LinkedIn profile to Clay: {profile_url}. Error: {str(e)}")
        return {"error": str(e)}

def save_linkedin_profile(profile_data: Dict[str, Any]) -> str:
    """
    Save LinkedIn profile data to a file.
    
    Args:
        profile_data: Profile data returned from Clay
        
    Returns:
        Path to the saved file
    """
    # Generate a filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    profile_id = profile_data.get('url', '').split('/')[-1] if 'url' in profile_data else 'unknown'
    filename = f"{profile_id}_{timestamp}.json"
    file_path = os.path.join(PROFILES_DIR, filename)
    
    # Save the profile data
    with open(file_path, 'w') as f:
        json.dump(profile_data, f, indent=2)
    
    logger.info(f"Saved LinkedIn profile data: {filename}")
    return file_path

def get_linkedin_profile_data(profile_url: str) -> Dict[str, Any]:
    """
    Get LinkedIn profile data either from Clay or from cached data.
    
    Args:
        profile_url: LinkedIn profile URL
        
    Returns:
        LinkedIn profile data
    """
    # First check if we already have this profile
    profile_id = profile_url.split('/')[-1]
    existing_profiles = [f for f in os.listdir(PROFILES_DIR) if f.startswith(profile_id) and f.endswith('.json')]
    
    if existing_profiles:
        # Use the most recent profile data
        latest_profile = sorted(existing_profiles)[-1]
        with open(os.path.join(PROFILES_DIR, latest_profile), 'r') as f:
            return json.load(f)
    
    # If not found, request from Clay
    response = send_linkedin_profile_to_clay(profile_url)
    
    # If Clay doesn't immediately return profile data (which is the usual case),
    # return a placeholder. The actual data would come via webhook callback.
    return {
        "url": profile_url,
        "status": "pending",
        "message": "Profile data requested from Clay. Will be available in subsequent runs."
    }