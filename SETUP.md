# Setup Guide for Lead Generation Agent with LinkedIn Access

This guide will walk you through setting up and using the Lead Generation Agent with LinkedIn profile access capability.

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

### Running the Lead Generation Agent

Run the agent with your lead criteria:

```bash
python -m deepresearch.run "VP of Engineering at Series B startups"
```

By default, the agent will perform 3 search loops. You can adjust this with the `--max-loops` parameter:

```bash
python -m deepresearch.run "Marketing Directors at Fortune 500 companies" --max-loops 5
```

### Example Lead Criteria

Here are some examples of effective lead criteria:

- "VP of Engineering at Series B startups in healthcare"
- "Marketing Directors at Fortune 500 companies"
- "Founders of AI startups in Europe"
- "Product Managers with fintech experience in New York"
- "CTOs of e-commerce companies with more than 50 employees"
- "Sales leaders in cybersecurity SaaS companies"

### How the LinkedIn Integration Works

1. The agent searches the web for leads matching your criteria
2. When it finds LinkedIn profile URLs in the search results, it sends them to Clay for enrichment
3. Clay processes the profiles and sends the enriched data back to your webhook endpoint
4. The data is stored locally and used in the lead generation process

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

### Lead Quality Issues

If you're not getting quality leads:

1. Try more specific criteria that include role, industry, and company size
2. Use terms that would appear on LinkedIn profiles
3. Increase the number of search loops with `--max-loops`
4. Try running multiple searches with slightly different criteria