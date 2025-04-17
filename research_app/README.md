# Deep Research Tool

A comprehensive research tool that combines SearXNG for web search, txtai for semantic indexing, and Google Gemini for report synthesis.

## Architecture

This application follows a modular architecture with the following components:

1. **SearXNG Integration**: Uses SearXNG as a privacy-focused meta search engine
2. **Content Processing**: Fetches, parses, cleans, and chunks content from various sources
3. **Semantic Indexing**: Uses txtai for local embeddings and semantic search
4. **Report Generation**: Leverages Google Gemini for synthesizing research reports

## API Endpoints

- `GET /`: Health check and service information
- `POST /search`: Search for information using SearXNG
- `POST /process`: Process and index URLs
- `POST /retrieve`: Retrieve relevant information for a query
- `POST /generate`: Generate a research report using Gemini
- `POST /workflow`: Execute a complete research workflow (search, process, generate)
- `GET /index-info`: Get information about the txtai index

## Getting Started

1. Set the GEMINI_API_KEY environment variable:
   ```
   export GEMINI_API_KEY=your_gemini_api_key_here
   ```

2. Start the services using Docker Compose:
   ```
   docker-compose up --build
   ```

3. The API will be available at http://localhost:5000

## Example Usage

### Complete Research Workflow

```bash
curl -X POST http://localhost:5000/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing recent developments",
    "max_urls": 10,
    "categories": "science,technology",
    "language": "en"
  }'
```

This will search, process, and generate a comprehensive research report on quantum computing.

## Components

- `app.py`: Main Flask application integrating all components
- `content_processor.py`: Handles fetching, parsing, and chunking content
- `txtai_manager.py`: Manages the semantic index for document retrieval
- `gemini_client.py`: Integrates with Google Gemini for report generation
- `searxng_client.py`: Client for interacting with SearXNG search
- `utils.py`: Utility functions for logging, formatting, and file operations
