# Setup Guide for Deep Research Agent with LinkedIn Access

This guide will walk you through setting up and using the Deep Research Agent with LinkedIn profile access capability.

## Prerequisites

1. Python 3.7 or higher
2. OpenAI API key
3. Tavily API key (for web search)
4. Clay API access (for LinkedIn profile enrichment)
5. Ngrok account (for receiving data from Clay)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/domse31/deepresearch.git
   cd deepresearch
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the example .env file and fill in your API keys:
   ```bash
   cp .env.example .env
   # Then edit .env with your API keys
   ```

## Configuration

### Setting up LinkedIn Profile Access

The agent uses Clay to access LinkedIn profile data. Follow these steps to set up access:

1. Start the LinkedIn service:
   ```bash
   python -m deepresearch.run --linkedin-service
   ```

2. In a separate terminal, start ngrok to create a public URL:
   ```bash
   ngrok http 8080
   ```

3. Copy the ngrok HTTPS URL and update the `CALLBACK_URL` in your `.env` file:
   ```
   CALLBACK_URL=https://your-ngrok-url.ngrok.io/webhook/clay-callback
   ```

4. Add your Clay webhook URL to the `.env` file:
   ```
   CLAY_WEBHOOK_URL=your_clay_webhook_url_here
   ```

## Usage

### Running the Research Agent

Run the agent with a research topic:

```bash
python -m deepresearch.run "Your research topic here"
```

By default, the agent will perform 3 research loops. You can adjust this with the `--max-loops` parameter:

```bash
python -m deepresearch.run "Your research topic here" --max-loops 5
```

### How the LinkedIn Integration Works

1. The agent searches the web for information on your research topic
2. When it finds LinkedIn profile URLs in the search results, it sends them to Clay for enrichment
3. Clay processes the profiles and sends the enriched data back to your webhook endpoint
4. The data is stored locally and used in subsequent research loops

The profile data is saved in the `linkedin_profiles` directory with timestamps, so you can review it later.

## Troubleshooting

### LinkedIn Service Issues

If the LinkedIn service doesn't receive profile data:

1. Check that ngrok is running and the URL is correct in your `.env` file
2. Verify that your Clay webhook URL is correct
3. Look at the logs in `linkedin_service.log` for error messages

### API Key Issues

If you get authentication errors:

1. Verify that all API keys are correctly set in your `.env` file
2. Check that your Clay webhook URL is correctly formatted
3. Make sure your ngrok session is active and the tunnel is working