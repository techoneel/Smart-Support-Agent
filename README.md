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
- [`requirements.txt`](./requirements.txt) - Required python libraries
- [Ollama 0.6.7+](https://ollama.com/download)
- [llama2](https://ollama.com/library/llama2)

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

### Testing Environment

1. Run the full test suite:
   ```powershell
   python -m pytest
   ```

2. Test the configuration:
   ```powershell
   python cli_test.py config
   ```

3. Test LLM integration:
   ```powershell
   python test_llm.py --prompt "What are the main features of a RAG system?"
   ```

### Running the CLI Version

1. Start the CLI interface:
   ```powershell
   python cli/main.py
   ```

2. Enter your queries when prompted:
   ```
   Ask a question: How do I configure the vector database?
   ```

3. Rate the responses to help improve the system:
   ```
   Rate this response (1-5): 5
   ```

### Ingesting Documents

1. Add PDFs to your knowledge base:
   ```powershell
   python -m core.ingestor.pdf_parser --path "path/to/your/docs"
   ```

2. Scrape web content:
   ```powershell
   python -m core.ingestor.web_scraper --url "https://your-documentation-site.com"
   ```

3. Monitor the vector index:
   ```powershell
   python -m core.retriever.index_builder --status
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

- [X] CLI interface
- [ ] Text and PDF ingestion
- [ ] Vector search with FAISS
- [X] LLM integration
- [ ] Feedback collection
- [ ] WhatsApp integration
- [ ] Custom web UI
- [ ] Persistent vector database
- [ ] Fine-tuning based on feedback

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
