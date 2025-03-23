# Deep Research Agent with LinkedIn Access

A powerful research agent that can access LinkedIn profiles during research tasks. It combines web search capabilities with the ability to retrieve enriched LinkedIn profile data through Clay.

## Features

- Deep web research on any topic
- LinkedIn profile access via Clay API
- Automatic summarization and knowledge gap identification
- Well-structured output with citations

## Setup

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Set environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export CLAY_WEBHOOK_URL=your_clay_webhook_url
   ```

3. Run the agent:
   ```
   python -m deepresearch.run "Your research topic"
   ```

## LinkedIn Profile Integration

The agent can recognize LinkedIn profile URLs in research results and automatically request enriched data through Clay's API.