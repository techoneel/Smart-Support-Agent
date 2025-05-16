import pytest
import os
import json
from unittest.mock import patch
from config.settings import Config

@pytest.fixture
def config_data(mock_config):
    return mock_config

@pytest.fixture
def test_config_file(temp_workspace, config_data):
    config_path = temp_workspace / "test_config.json"
    with open(config_path, 'w') as f:
        json.dump(config_data, f)
    return str(config_path)

class TestConfig:
    def test_init_with_defaults(self):
        # Act
        config = Config()
        
        # Assert
        assert config.channel == "cli"
        assert config.llm_provider == "ollama"
        assert config.embedding_dim == 768
    
    def test_init_with_custom_values(self, config_data):
        # Act
        config = Config(**config_data)
        
        # Assert
        assert config.channel == config_data["channel"]
        assert config.llm_provider == config_data["llm_provider"]
        assert config.llm_api_key == config_data["llm_api_key"]
        assert config.embedding_dim == config_data["embedding_dim"]
    
    @patch.dict(os.environ, {
        "SSA_CHANNEL": "web",
        "SSA_LLM_PROVIDER": "openai",
        "SSA_LLM_API_KEY": "test_key",
        "SSA_EMBEDDING_DIM": "512"
    })
    def test_from_env(self):
        # Act
        config = Config.from_env()
        
        # Assert
        assert config.channel == "web"
        assert config.llm_provider == "openai"
        assert config.llm_api_key == "test_key"
        assert config.embedding_dim == 512
    
    def test_from_file(self, test_config_file, config_data):
        # Act
        config = Config.from_file(test_config_file)
        
        # Assert
        assert config.channel == config_data["channel"]
        assert config.llm_provider == config_data["llm_provider"]
        assert config.embedding_dim == config_data["embedding_dim"]
    
    def test_to_dict(self, config_data):
        # Arrange
        config = Config(**config_data)
        
        # Act
        result = config.to_dict()
        
        # Assert
        assert result == config_data
    
    def test_save(self, temp_workspace, config_data):
        # Arrange
        config = Config(**config_data)
        save_path = str(temp_workspace / "saved_config.json")
        
        # Act
        config.save(save_path)
        
        # Assert
        assert os.path.exists(save_path)
        with open(save_path) as f:
            saved_data = json.load(f)
        assert saved_data == config_data
    
    def test_create_directories(self, temp_workspace):
        # Arrange
        config = Config(
            vector_db_path=str(temp_workspace / "vectors/index"),
            feedback_log_path=str(temp_workspace / "logs/feedback.log")
        )
        
        # Assert
        assert os.path.exists(os.path.dirname(config.vector_db_path))
        assert os.path.exists(os.path.dirname(config.feedback_log_path))
