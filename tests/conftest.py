import os
import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_pdf_content():
    """Sample PDF content for testing."""
    return "This is sample PDF content for testing purposes."

@pytest.fixture
def mock_web_content():
    """Sample web content for testing."""
    return {
        'content': 'This is sample web content for testing purposes.',
        'metadata': {
            'url': 'https://example.com',
            'title': 'Example Page',
            'description': 'An example page for testing'
        }
    }

@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    config = MagicMock()
    config.vector_db_path = "data/test_index"
    config.feedback_log_path = "logs/test_feedback.log"
    config.llm_provider = "ollama"
    config.llm_api_key = ""
    config.channel = "cli"
    return config