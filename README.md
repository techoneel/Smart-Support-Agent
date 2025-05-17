# Smart Support Agent

A flexible and extensible customer support automation system with advanced document retrieval and natural language understanding capabilities.

## Overview

Smart Support Agent is a RAG (Retrieval Augmented Generation) system designed to provide accurate answers to customer queries by leveraging your knowledge base. The agent retrieves relevant information from your documents and uses large language models to generate helpful responses, with a current test coverage of 93%.

## Features

- **Document Ingestion**: Automatically process PDFs and web content
- **Vector Search**: Fast and accurate semantic search using FAISS
- **Multiple Interfaces**: Easily switch between CLI, WhatsApp, or custom web UI
- **Feedback Collection**: Capture user ratings to improve system quality
- **Flexible Architecture**: Clean, modular design for easy extension
- **High Test Coverage**: Comprehensive test suite with 93% coverage
- **Extensible Design**: Easy to add new document types and interfaces

## Quick Start

### Prerequisites

- [Python 3.9+](https://www.python.org/downloads/)
- One of the following LLM providers:
  - [Ollama](https://ollama.com/download) (local, no API key required)
  - [Google Gemini API key](https://ai.google.dev/) (cloud-based)
  - [OpenAI API key](https://platform.openai.com/) (cloud-based)
  - [Together.ai API key](https://together.ai/) (cloud-based)

### Installation

#### Automatic Setup (Recommended)

Choose the appropriate setup script for your operating system:

**Windows:**
```
setup.bat
```
or with PowerShell:
```
.\dev-setup.ps1
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Using Make (Unix systems):**
```bash
make setup
```

#### Manual Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-support-agent.git
cd smart-support-agent

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
pip install -e ".[dev]"  # For development

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Configuration

Edit `.env` to configure your LLM provider:

#### For Ollama (local, no API key required):
```
SSA_LLM_PROVIDER=ollama
SSA_LLM_API_KEY=
SSA_LLM_MODEL=llama2
```

#### For Google Gemini:
```
SSA_LLM_PROVIDER=gemini
SSA_LLM_API_KEY=your_gemini_api_key_here
SSA_LLM_MODEL=gemini-2.0-flash
```

#### For OpenAI:
```
SSA_LLM_PROVIDER=openai
SSA_LLM_API_KEY=your_openai_api_key_here
SSA_LLM_MODEL=gpt-3.5-turbo
```

### CLI Commands

The Smart Support Agent provides several CLI commands to help you manage and use the system:

```bash
# Show all available commands
python cli/main.py --help
```

#### Setup Command

Use the setup command to ingest documents into your knowledge base:

```bash
python cli/main.py setup [--debug] [--no-js]
```

Options:
- `--debug`: Enable debug mode with detailed error messages
- `--no-js`: Disable JavaScript rendering for web scraping

This interactive command will:
- Guide you through adding PDF documents (files or directories)
- Help you scrape web content (single pages or entire sites)
- Process and index all content for retrieval

#### Run Command

Start the interactive support agent:

```bash
python cli/main.py run [OPTIONS]
```

Options:
- `--config-path CONFIG_PATH`: Path to a custom configuration file
- `--provider PROVIDER`: Override LLM provider (ollama, gemini, openai, together)
- `--model MODEL`: Override LLM model
- `--api-key API_KEY`: Override API key for cloud providers

Examples:
```bash
# Run with default configuration
python cli/main.py run

# Run with Gemini API
python cli/main.py run --provider gemini --api-key YOUR_API_KEY --model gemini-2.0-flash

# Run with OpenAI
python cli/main.py run --provider openai --api-key YOUR_API_KEY --model gpt-3.5-turbo
```

#### View Index Command

View and export the FAISS index for visualization:

```bash
python cli/main.py view_index [OPTIONS]
```

Options:
- `--export FILENAME`: Export index to a JSON file for visualization
- `--limit N`: Limit the number of vectors to display/export (default: 10)
- `--index-path PATH`: Path to the FAISS index file

#### Stats Command

View usage statistics for your support agent:

```bash
python cli/main.py stats
```

### Development

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=core --cov=cli --cov=config --cov=factory

# On Unix systems with Make
make test
```

#### Linting and Formatting

```bash
# Run linters
flake8 core cli config factory
black core cli config factory
mypy core cli config factory

# On Unix systems with Make
make lint
```

## Architecture

The Smart Support Agent follows clean architecture principles, with clear separation between:

- Core business logic
- Interface adapters
- External services

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed information about the system design.

## Extending the System

### Adding New Input/Output Channels

1. Implement the `InputHandler` and `OutputHandler` interfaces
2. Register your new channel in the factory
3. Update the configuration to use your new channel

### Supporting New Document Types

1. Create a new parser in the `ingestor` package
2. Implement the chunking and extraction logic
3. Pass the extracted content to the index builder

### Adding New LLM Providers

1. Update the `LLMClient` class in `core/llm/llm_client.py`
2. Implement the provider-specific API call method
3. Update the configuration to use your new provider

## Troubleshooting

### Ollama Connection Issues

If you encounter errors connecting to Ollama:

1. Make sure Ollama is installed and running
2. Check if the model is available with `ollama list`
3. Pull the model if needed with `ollama pull llama2`
4. Consider using a cloud provider instead with the `--provider` option

### PDF Processing Issues

If you encounter errors processing PDFs:

1. Use the `--debug` flag to get detailed error information
2. Check if the PDF is password-protected or encrypted
3. For scanned PDFs, use OCR software to extract text first
4. Try converting the PDF to a different format

### Web Scraping Issues

If you encounter errors with web scraping:

1. Try using the `--no-js` flag to disable JavaScript rendering
2. Check if the website allows scraping (some sites block bots)
3. Verify your internet connection
4. Try a different URL or website

## License

This project is licensed under the MIT License - see the LICENSE file for details.