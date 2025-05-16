import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch
from cli.main import cli

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

@pytest.fixture
def mock_agent():
    """Create a mock support agent."""
    agent = Mock()
    agent.handle_query.return_value = "Test response"
    return agent

class TestCLICommands:
    def test_run_command_with_config_file(self, mock_config, mock_agent):
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
            mock_input = Mock()
            mock_output = Mock()
            mock_factory.create_channel.return_value = (mock_input, mock_output)
            mock_agent_class.return_value = mock_agent
            mock_input.get_user_query.side_effect = ["test query", "quit"]
            
            # Run command
            result = runner.invoke(cli, ['run', '--config-path', 'test_config.json'])
            
            # Assert success
            assert result.exit_code == 0
            mock_config_class.from_file.assert_called_once()
            mock_input.get_user_query.assert_called()
            mock_output.display_response.assert_called_with("Test response")
    
    def test_run_command_with_env_config(self, mock_config, mock_agent):
        runner = CliRunner()
        
        with patch('cli.main.Config') as mock_config_class, \
             patch('cli.main.ChannelFactory') as mock_factory, \
             patch('cli.main.LLMClient'), \
             patch('cli.main.SearchEngine'), \
             patch('cli.main.SupportAgent') as mock_agent_class, \
             patch('cli.main.FeedbackCollector'):
             
            # Set up mocks
            mock_config_class.from_env.return_value = mock_config
            mock_input = Mock()
            mock_output = Mock()
            mock_factory.create_channel.return_value = (mock_input, mock_output)
            mock_agent_class.return_value = mock_agent
            mock_input.get_user_query.side_effect = ["test query", "quit"]
            
            # Run command
            result = runner.invoke(cli, ['run'])
            
            # Assert success
            assert result.exit_code == 0
            mock_config_class.from_env.assert_called_once()
    
    def test_run_command_handles_query_error(self, mock_config):
        runner = CliRunner()
        
        with patch('cli.main.Config') as mock_config_class, \
             patch('cli.main.ChannelFactory') as mock_factory, \
             patch('cli.main.LLMClient'), \
             patch('cli.main.SearchEngine'), \
             patch('cli.main.SupportAgent') as mock_agent_class, \
             patch('cli.main.FeedbackCollector'):
             
            # Set up mocks
            mock_config_class.from_env.return_value = mock_config
            mock_input = Mock()
            mock_output = Mock()
            mock_factory.create_channel.return_value = (mock_input, mock_output)
            mock_agent = Mock()
            mock_agent.handle_query.side_effect = Exception("Test error")
            mock_agent_class.return_value = mock_agent
            mock_input.get_user_query.side_effect = ["test query", "quit"]
            
            # Run command
            result = runner.invoke(cli, ['run'])
            
            # Assert error handling
            assert result.exit_code == 0
            mock_output.display_error.assert_called_with("Test error")
    
    def test_stats_command_with_ratings(self, mock_config):
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
            mock_collector = Mock()
            mock_collector.get_feedback_stats.return_value = stats_data
            mock_collector_class.return_value = mock_collector
            
            # Run command
            result = runner.invoke(cli, ['stats'])
            
            # Assert success
            assert result.exit_code == 0
            assert "Total Queries: 10" in result.output
            assert "Average Rating: 4.50" in result.output
            
    def test_stats_command_without_ratings(self, mock_config):
        runner = CliRunner()
        
        stats_data = {
            'total_queries': 5,
            'rated_queries': 0,
            'average_rating': None
        }
        
        with patch('cli.main.Config') as mock_config_class, \
             patch('cli.main.FeedbackCollector') as mock_collector_class:
             
            # Set up mocks
            mock_config_class.from_env.return_value = mock_config
            mock_collector = Mock()
            mock_collector.get_feedback_stats.return_value = stats_data
            mock_collector_class.return_value = mock_collector
            
            # Run command
            result = runner.invoke(cli, ['stats'])
            
            # Assert success
            assert result.exit_code == 0
            assert "Total Queries: 5" in result.output
            assert "Average Rating: No ratings yet" in result.output
    
    def test_stats_command_error_handling(self):
        runner = CliRunner()
        
        with patch('cli.main.Config') as mock_config_class:
            # Set up mock to raise an error
            mock_config_class.from_env.side_effect = Exception("Test error")
            
            # Run command
            result = runner.invoke(cli, ['stats'])
            
            # Assert error handling
            assert result.exit_code == 0
            assert "Error: Test error" in result.output
