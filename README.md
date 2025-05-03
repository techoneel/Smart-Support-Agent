# Smart Support Agent

A flexible and extensible customer support automation system with advanced document retrieval and natural language understanding capabilities.

## Overview

Smart Support Agent is a RAG (Retrieval Augmented Generation) system designed to provide accurate answers to customer queries by leveraging your knowledge base. The agent retrieves relevant information from your documents and uses large language models to generate helpful responses.

## Features

- **Document Ingestion**: Automatically process PDFs and web content
- **Vector Search**: Fast and accurate semantic search using FAISS
- **Multiple Interfaces**: Easily switch between CLI, WhatsApp, or custom web UI
- **Feedback Collection**: Capture user ratings to improve system quality
- **Flexible Architecture**: Clean, modular design for easy extension

## Quick Start

### Prerequisites

- Python 3.9+
- Required libraries (see `requirements.txt`)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-support-agent.git
cd smart-support-agent

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Configuration

Edit `config/settings.py` or use environment variables to configure:

- LLM provider and API keys
- Vector database settings
- Input/output channels
- Logging preferences

### Running the CLI Version

```bash
python cli/main.py
```

### Ingesting Documents

```bash
# Add PDFs to your knowledge base
python -m core.ingestor.pdf_parser --path /path/to/your/docs

# Scrape web content
python -m core.ingestor.web_scraper --url https://your-documentation-site.com
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

## Roadmap

- [ ] CLI interface
- [ ] Text and PDF ingestion
- [ ] Vector search with FAISS
- [ ] LLM integration
- [ ] Feedback collection
- [ ] WhatsApp integration
- [ ] Custom web UI
- [ ] Persistent vector database
- [ ] Fine-tuning based on feedback

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
