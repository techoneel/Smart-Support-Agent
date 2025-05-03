# Smart Support Agent Architecture

This document provides an in-depth look at the architecture and design principles of the Smart Support Agent.

## Design Philosophy

The Smart Support Agent is built on the principles of clean architecture, with clear separation of concerns and dependency inversion:

1. **Core Domain**: Contains business logic independent of external systems
2. **Interface Adapters**: Handle communication with users and external services
3. **Factory Pattern**: Enables flexible configuration and testing
4. **Open for Extension**: Easy to add new channels or document types

## Directory Structure

```
smart-support-agent/
├── core/
│   ├── interface/
│   │   ├── input_handler.py       # Abstract base class for input channels
│   │   └── output_handler.py      # Abstract base class for output channels
│   ├── agents/
│   │   ├── support_agent.py       # Core Agent Logic (retrieval + LLM)
│   │   └── feedback_collector.py  # Feedback logger
│   ├── retriever/
│   │   ├── index_builder.py       # Chunk + embed + store
│   │   └── search_engine.py       # FAISS vector search
│   ├── ingestor/
│   │   ├── web_scraper.py         # Website content extraction
│   │   └── pdf_parser.py          # PDF extraction
│   └── llm/
│       └── llm_client.py          # Abstraction over LLM providers
├── cli/
│   └── main.py                    # CLI entrypoint using factory
├── factory/
│   └── channel_factory.py         # Factory to initialize input/output
├── config/
│   └── settings.py                # Config and environment management
├── logs/
│   └── feedback.log               # Saved customer ratings and queries
└── requirements.txt
```

## Component Details

### Core Components

#### Interface Layer (`core/interface/`)

Defines abstract base classes that all input and output channels must implement:

```python
# core/interface/input_handler.py
class InputHandler:
    def get_user_query(self) -> str:
        raise NotImplementedError()
    
    def get_feedback(self, response: str) -> int:
        raise NotImplementedError()

# core/interface/output_handler.py
class OutputHandler:
    def display_response(self, response: str) -> None:
        raise NotImplementedError()
    
    def display_error(self, error: str) -> None:
        raise NotImplementedError()
```

#### Agents (`core/agents/`)

Contains the main business logic for the support agent:

```python
# core/agents/support_agent.py (simplified)
class SupportAgent:
    def __init__(self, retriever, llm_client):
        self.retriever = retriever
        self.llm_client = llm_client
        
    def handle_query(self, query: str) -> str:
        # 1. Retrieve relevant documents
        docs = self.retriever.search(query)
        
        # 2. Generate response using LLM
        prompt = self._build_prompt(query, docs)
        response = self.llm_client.generate(prompt)
        
        return response
```

The `feedback_collector.py` module logs user queries and feedback for future analysis.

#### Retriever (`core/retriever/`)

Handles vector search functionality:

- `index_builder.py`: Creates and updates the vector index
- `search_engine.py`: Performs semantic search with FAISS

#### Ingestor (`core/ingestor/`)

Processes different document types:

- `web_scraper.py`: Extracts content from websites
- `pdf_parser.py`: Extracts text from PDF documents

#### LLM Client (`core/llm/`)

Provides a unified interface to different LLM providers:

```python
# core/llm/llm_client.py
class LLMClient:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        
    def generate(self, prompt: str) -> str:
        if self.provider == "together":
            return self._call_together_ai(prompt)
        elif self.provider == "ollama":
            return self._call_ollama(prompt)
        # Add more providers as needed
```

### CLI Interface

The CLI interface implements the `InputHandler` and `OutputHandler` interfaces:

```python
# cli/cli_handler.py
class CLIInputHandler(InputHandler):
    def get_user_query(self) -> str:
        return input("Ask a question: ")
    
    def get_feedback(self, response: str) -> int:
        rating = input("Rate this response (1-5): ")
        return int(rating)

class CLIOutputHandler(OutputHandler):
    def display_response(self, response: str) -> None:
        print(f"\nAnswer: {response}\n")
    
    def display_error(self, error: str) -> None:
        print(f"Error: {error}")
```

### Factory Pattern

The factory pattern is used to instantiate the appropriate input/output handlers:

```python
# factory/channel_factory.py
class ChannelFactory:
    @staticmethod
    def create_channel(channel_type: str):
        if channel_type == "cli":
            return (CLIInputHandler(), CLIOutputHandler())
        elif channel_type == "whatsapp":
            return (WhatsAppInputHandler(), WhatsAppOutputHandler())
        elif channel_type == "web":
            return (WebInputHandler(), WebOutputHandler())
        else:
            raise ValueError(f"Unknown channel type: {channel_type}")
```

### Main Flow

```python
# cli/main.py
def main():
    # Load configuration
    config = Config.from_env()
    
    # Initialize components via factory
    input_handler, output_handler = ChannelFactory.create_channel(config.channel)
    
    # Initialize core components
    retriever = SearchEngine(config.vector_db_path)
    llm_client = LLMClient(config.llm_provider, config.llm_api_key)
    
    # Create agent
    agent = SupportAgent(retriever, llm_client)
    feedback_collector = FeedbackCollector(config.feedback_log_path)
    
    # Main loop
    while True:
        try:
            # Get user query
            query = input_handler.get_user_query()
            if query.lower() == "quit":
                break
                
            # Process query
            response = agent.handle_query(query)
            
            # Display response
            output_handler.display_response(response)
            
            # Collect feedback
            rating = input_handler.get_feedback(response)
            feedback_collector.log_feedback(query, response, rating)
            
        except Exception as e:
            output_handler.display_error(str(e))
```

## Future Extensions

### WhatsApp Integration

To add WhatsApp support, you would:

1. Create WhatsApp handlers:
```python
class WhatsAppInputHandler(InputHandler):
    def __init__(self, webhook_client):
        self.webhook_client = webhook_client
        
    def get_user_query(self) -> str:
        # Get message from webhook
        return self.webhook_client.get_latest_message()
    
    def get_feedback(self, response: str) -> int:
        # Implement feedback collection via WhatsApp
        pass

class WhatsAppOutputHandler(OutputHandler):
    def __init__(self, whatsapp_client):
        self.whatsapp_client = whatsapp_client
        
    def display_response(self, response: str) -> None:
        self.whatsapp_client.send_message(response)
```

2. Register these handlers in the factory:
```python
# Update factory/channel_factory.py to include WhatsApp
if channel_type == "whatsapp":
    webhook_client = WhatsAppWebhookClient(config.whatsapp_webhook_url)
    whatsapp_client = WhatsAppClient(config.whatsapp_api_key)
    return (WhatsAppInputHandler(webhook_client), 
            WhatsAppOutputHandler(whatsapp_client))
```

### Custom Web UI

For a web interface:

1. Create a lightweight Flask backend with REST endpoints
2. Implement Web handlers that communicate via this API
3. Build a React frontend that calls the Flask API

## Performance Considerations

- Vector search is optimized using FAISS for fast similarity search
- Document chunking strategies balance retrieval quality and index size
- API calls to LLM providers are abstracted to support caching and retries

## Testing Strategy

The clean architecture enables thorough testing at each level:

- **Unit Tests**: Core business logic can be tested independently
- **Integration Tests**: Verify interactions between components
- **End-to-End Tests**: Test the complete workflow with mock interfaces

## Conclusion

The Smart Support Agent architecture provides a robust foundation for building extensible customer support automation. By following clean architecture principles, the system can evolve over time while maintaining a clear separation of concerns.
