import pytest
from unittest.mock import Mock, patch
import requests
from core.llm.llm_client import LLMClient

@pytest.fixture
def llm_client():
    return LLMClient("ollama", api_key="test_key", model="test_model")

class TestLLMClient:
    def test_init_defaults(self):
        # Act
        client = LLMClient("ollama")
        
        # Assert
        assert client.provider == "ollama"
        assert client.model == "llama2"  # Default model for ollama
    
    def test_init_custom_model(self):
        # Act
        client = LLMClient("together", model="mixtral")
        
        # Assert
        assert client.provider == "together"
        assert client.model == "mixtral"
    
    @patch('requests.post')
    def test_generate_together(self, mock_post):
        # Arrange
        client = LLMClient("together", "test_key")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"text": "Generated response"}]
        }
        mock_post.return_value = mock_response
        
        # Act
        response = client.generate("Test prompt")
        
        # Assert
        assert response == "Generated response"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_ollama(self, mock_post):
        # Arrange
        client = LLMClient("ollama")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = [
            b'{"response": "Gen"}',
            b'{"response": "erated"}',
            b'{"response": " response"}'
        ]
        mock_post.return_value = mock_response
        
        # Act
        response = client.generate("Test prompt")
        
        # Assert
        assert response == "Generated response"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_openai(self, mock_post):
        # Arrange
        client = LLMClient("openai", "test_key")
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "Generated response"}
            }]
        }
        mock_post.return_value = mock_response
        
        # Act
        response = client.generate("Test prompt")
        
        # Assert
        assert response == "Generated response"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generate_error_handling(self, mock_post):
        # Arrange
        client = LLMClient("together", "test_key")
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Error message"
        mock_post.return_value = mock_response
        
        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            client.generate("Test prompt")
        assert "API call failed" in str(exc_info.value)
    
    def test_invalid_provider(self):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            LLMClient("invalid_provider").generate("Test prompt")
        assert "Unsupported provider" in str(exc_info.value)
