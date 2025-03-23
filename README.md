# Lead Generation Agent with LinkedIn Access

A powerful lead generation agent that can access LinkedIn profiles to identify and enrich potential leads. It combines web search capabilities with LinkedIn profile data retrieval through Clay.

## Features

- Automated lead generation based on your specific criteria
- LinkedIn profile access and enrichment via Clay API
- Structured lead information with contact details when available
- Automatic identification of gaps in lead coverage

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

6. Run the lead generation agent:
   ```
   python -m deepresearch.run "startup CTOs in fintech"
   ```

## How It Works

1. **Query Generation**: The agent creates an optimized search query based on your lead criteria.
2. **Web Search**: It searches the web for potential leads matching your criteria using Tavily.
3. **LinkedIn Detection**: When LinkedIn profile URLs are found, they're sent to Clay for enrichment.
4. **Lead Compilation**: The agent compiles all information into a structured lead list.
5. **Gap Analysis**: The agent identifies missing lead types and performs additional searches.

## Example Lead Criteria

The agent works best with specific lead criteria such as:

- "VP of Engineering at Series B startups in healthcare"
- "Marketing Directors at Fortune 500 companies"
- "Founders of AI startups in Europe"
- "Product Managers with fintech experience in New York"

## LinkedIn Integration

The agent:
- Detects LinkedIn profile URLs in search results
- Sends profiles to Clay for enrichment
- Receives detailed profile data including current role, company, skills
- Incorporates profile information into the lead list

LinkedIn profile data is stored in the `linkedin_profiles` directory for future reference.

## Example Usage

Try running the included example script:

```
python example.py
```

This will:
1. Start the LinkedIn service
2. Guide you through setting up ngrok
3. Let you enter lead criteria
4. Run the lead generation agent and show the results

## Configuration

You can configure the agent through environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `TAVILY_API_KEY`: Your Tavily API key for web search
- `CLAY_WEBHOOK_URL`: Your Clay webhook URL
- `CALLBACK_URL`: Your ngrok URL for receiving data from Clay

## Command Line Options

```
python -m deepresearch.run --help
```

Options include:
- `--linkedin-service`: Start the LinkedIn service
- `--port`: Specify the port for the LinkedIn service
- `--max-loops`: Set the maximum number of search loops

## Detailed Setup

For detailed setup instructions, see [SETUP.md](SETUP.md).