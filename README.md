# Deep Research Agent with LinkedIn Access

A powerful research agent that can access LinkedIn profiles during research tasks. It combines web search capabilities with the ability to retrieve enriched LinkedIn profile data through Clay.

## Features

- Deep web research on any topic
- LinkedIn profile access via Clay API
- Automatic summarization and knowledge gap identification
- Well-structured output with citations

## Quick Start

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and add your API keys:
   ```
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Start the LinkedIn service:
   ```
   python -m deepresearch.run --linkedin-service
   ```

4. In another terminal, start ngrok:
   ```
   ngrok http 8080
   ```

5. Update your `.env` file with the ngrok URL:
   ```
   CALLBACK_URL=https://your-ngrok-url.ngrok.io/webhook/clay-callback
   ```

6. Run the agent:
   ```
   python -m deepresearch.run "Your research topic"
   ```

## How It Works

1. **Search Query Generation**: The agent generates an optimized search query based on your research topic.
2. **Web Research**: It searches the web for relevant information using Tavily.
3. **LinkedIn Detection**: If LinkedIn profile URLs are found in the search results, they are automatically sent to Clay for enrichment.
4. **Data Enrichment**: Clay processes the LinkedIn profiles and returns detailed data.
5. **Summarization**: All gathered information is summarized into a comprehensive research report.
6. **Knowledge Gap Analysis**: The agent identifies areas for further research and performs additional searches.

## LinkedIn Integration

The agent can:
- Detect LinkedIn profile URLs in search results
- Send profiles to Clay for enrichment
- Receive and store the enriched profile data
- Incorporate profile information into the research summary

LinkedIn profile data is stored in the `linkedin_profiles` directory for future reference.

## Example Usage

Try running the included example script:

```
python example.py
```

This will:
1. Start the LinkedIn service
2. Guide you through setting up ngrok
3. Let you enter a research topic
4. Run the research agent and show the results

## Detailed Setup

For detailed setup instructions, see [SETUP.md](SETUP.md).

## Configuration

You can configure the agent through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily API key for web search
- `CLAY_WEBHOOK_URL`: Your Clay webhook URL
- `CALLBACK_URL`: Your ngrok URL for receiving data from Clay
- `LANGSMITH_API_KEY` (optional): For LangSmith tracing

## Command Line Options

The agent supports several command line options:

```
python -m deepresearch.run --help
```

Options include:
- `--linkedin-service`: Start the LinkedIn service
- `--port`: Specify the port for the LinkedIn service
- `--max-loops`: Set the maximum number of research loops