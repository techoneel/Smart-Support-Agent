import pytest
from unittest.mock import Mock, patch
from click.testing import CliRunner
from cli.main import cli, run, stats

@pytest.fixture
def mock_components():
    """Create mock components for testing."""
    input_handler = Mock()
    output_handler = Mock()
    llm_client = Mock()
    search_engine = Mock()
    agent = Mock()
    feedback_collector = Mock()
    
    return {
        'input_handler': input_handler,
        'output_handler': output_handler,
        'llm_client': llm_client,
        'search_engine': search_engine,
        'agent': agent,
        'feedback_collector': feedback_collector
    }

@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = Mock()
    config.channel = "cli"
    config.llm_provider = "ollama"
    config.llm_api_key = "test_key"
    config.vector_db_path = "test_vectors"
    config.feedback_log_path = "test_feedback.log"
    return config

class TestCLIMain:
    def test_run_command_with_config_file(self, mock_components, mock_config):
        runner = CliRunner()
        
        with patch('cli.main.Config') as mock_config_class, \
             patch('cli.main.ChannelFactory') as mock_factory, \
             patch('cli.main.LLMClient') as mock_llm_class, \
             patch('cli.main.SearchEngine') as mock_search_class, \
             patch('cli.main.SupportAgent') as mock_agent_class, \
             patch('cli.main.FeedbackCollector') as mock_collector_class, \
             patch('os.path.exists', return_value=True):
            
            # Set up mocks
            mock_config_class.from_file.return_value = mock_config
            mock_factory.create_channel.return_value = (
                mock_components['input_handler'],
                mock_components['output_handler']
            )
            mock_components['input_handler'].get_user_query.side_effect = ["test query", "quit"]
            mock_components['agent'].handle_query.return_value = "test response"
            
            # Run command
            result = runner.invoke(cli, ['run', '--config-path', 'test_config.json'])
            
            # Assert
            assert result.exit_code == 0
            mock_config_class.from_file.assert_called_once()
            mock_factory.create_channel.assert_called_once()
            mock_components['input_handler'].get_user_query.assert_called()
            mock_components['output_handler'].display_response.assert_called()
    
    def test_run_command_with_env_config(self, mock_components, mock_config):
        runner = CliRunner()
        
        with patch('cli.main.Config') as mock_config_class, \
             patch('cli.main.ChannelFactory') as mock_factory, \
             patch('cli.main.LLMClient') as mock_llm_class, \
             patch('cli.main.SearchEngine') as mock_search_class, \
             patch('cli.main.SupportAgent') as mock_agent_class, \
             patch('cli.main.FeedbackCollector') as mock_collector_class:
            
            # Set up mocks
            mock_config_class.from_env.return_value = mock_config
            mock_factory.create_channel.return_value = (
                mock_components['input_handler'],
                mock_components['output_handler']
            )
            mock_components['input_handler'].get_user_query.side_effect = ["test query", "quit"]
            mock_components['agent'].handle_query.return_value = "test response"
            
            # Run command
            result = runner.invoke(cli, ['run'])
            
            # Assert
            assert result.exit_code == 0
            mock_config_class.from_env.assert_called_once()
            mock_factory.create_channel.assert_called_once()
    
    def test_run_command_error_handling(self, mock_components, mock_config):
        runner = CliRunner()
        
        with patch('cli.main.Config') as mock_config_class:
            # Set up mock to raise an exception
            mock_config_class.from_env.side_effect = Exception("Test error")
            
            # Run command
            result = runner.invoke(cli, ['run'])
            
            # Assert
            assert result.exit_code == 0  # Click catches exceptions
            assert "Error: Test error" in result.output
    
    def test_stats_command(self, mock_config):
        runner = CliRunner()
        
        stats_data = {
            'total_queries': 10,
            'rated_queries': 8,
            'average_rating': 4.5
        }
        
        with patch('cli.main.Config') as mock_config_class, \
             patch('cli.main.FeedbackCollector') as mock_collector_class:
            
            # Set up mocks
            mock_config_class.from_env.return_value = mock_config
            mock_collector = mock_collector_class.return_value
            mock_collector.get_feedback_stats.return_value = stats_data
            
            # Run command
            result = runner.invoke(cli, ['stats'])
            
            # Assert
            assert result.exit_code == 0
            assert "Total Queries: 10" in result.output
            assert "Average Rating: 4.50" in result.output
            
    def test_stats_command_no_ratings(self, mock_config):
        runner = CliRunner()
        
        stats_data = {
            'total_queries': 10,
            'rated_queries': 0,
            'average_rating': None
        }
        
        with patch('cli.main.Config') as mock_config_class, \
             patch('cli.main.FeedbackCollector') as mock_collector_class:
            
            # Set up mocks
            mock_config_class.from_env.return_value = mock_config
            mock_collector = mock_collector_class.return_value
            mock_collector.get_feedback_stats.return_value = stats_data
            
            # Run command
            result = runner.invoke(cli, ['stats'])
            
            # Assert
            assert result.exit_code == 0
            assert "No ratings yet" in result.output
