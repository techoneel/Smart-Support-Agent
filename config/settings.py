import os
from pathlib import Path
from typing import Optional
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration manager for the application."""
    
    def __init__(
        self,
        channel: str = "cli",
        llm_provider: str = "ollama",
        llm_api_key: str = "",
        llm_model: Optional[str] = None,
        vector_db_path: Optional[str] = None,
        feedback_log_path: str = "logs/feedback.log",
        embedding_dim: int = 768,
        api_host: str = "127.0.0.1",
        api_port: int = 8000
    ):
        """Initialize configuration.
        
        Args:
            channel (str): Input/output channel ("cli", "whatsapp", "web")
            llm_provider (str): LLM provider ("together", "ollama", "openai")
            llm_api_key (str): API key for the LLM provider
            llm_model (Optional[str]): Model name
            vector_db_path (Optional[str]): Path to the vector database
            feedback_log_path (str): Path to the feedback log
            embedding_dim (int): Dimension of embeddings
            api_host (str): Host for the API server
            api_port (int): Port for the API server
        """
        self.channel = channel
        self.llm_provider = llm_provider
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model
        self.vector_db_path = str(Path(vector_db_path)) if vector_db_path else None
        self.feedback_log_path = str(Path(feedback_log_path)) if feedback_log_path else None
        self.embedding_dim = embedding_dim
        self.api_host = api_host
        self.api_port = api_port
        
        # Create necessary directories if paths are provided and valid
        if self.feedback_log_path and os.path.dirname(self.feedback_log_path):
            os.makedirs(os.path.dirname(self.feedback_log_path), exist_ok=True)
        
        if self.vector_db_path and os.path.dirname(self.vector_db_path):
            os.makedirs(os.path.dirname(self.vector_db_path), exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables.
        
        Returns:
            Config: Configuration object
        """
        return cls(
            channel=os.getenv("SSA_CHANNEL", "cli"),
            llm_provider=os.getenv("SSA_LLM_PROVIDER", "ollama"),
            llm_api_key=os.getenv("SSA_LLM_API_KEY", ""),
            llm_model=os.getenv("SSA_LLM_MODEL"),
            vector_db_path=os.getenv("SSA_VECTOR_DB_PATH"),
            feedback_log_path=os.getenv("SSA_FEEDBACK_LOG_PATH", "logs/feedback.log"),
            embedding_dim=int(os.getenv("SSA_EMBEDDING_DIM", "768")),
            api_host=os.getenv("SSA_API_HOST", "127.0.0.1"),
            api_port=int(os.getenv("SSA_API_PORT", "8000"))
        )
    
    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """Create configuration from a JSON file.
        
        Args:
            path (str): Path to the configuration file
            
        Returns:
            Config: Configuration object
        """
        path = Path(path)
        with path.open('r') as f:
            config_data = json.load(f)
        
        return cls(**config_data)
    
    def to_dict(self) -> dict:
        """Convert configuration to dictionary.
        
        Returns:
            dict: Configuration as dictionary
        """
        return {
            "channel": self.channel,
            "llm_provider": self.llm_provider,
            "llm_api_key": self.llm_api_key,
            "llm_model": self.llm_model,
            "vector_db_path": self.vector_db_path,
            "feedback_log_path": self.feedback_log_path,
            "embedding_dim": self.embedding_dim,
            "api_host": self.api_host,
            "api_port": self.api_port
        }

    def save(self, path: str) -> None:
        """Save configuration to a JSON file.
        
        Args:
            path (str): Path where to save the configuration
        """
        path = Path(path)
        if path.parent:
            os.makedirs(path.parent, exist_ok=True)
        with path.open('w') as f:
            json.dump(self.to_dict(), f, indent=2)