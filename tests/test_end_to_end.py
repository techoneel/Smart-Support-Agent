import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from cli.main import cli

class TestEndToEnd:
    """End-to-end tests for the CLI workflow."""
    
    @pytest.fixture
    def mock_environment(self):
        """Set up a mock environment for end-to-end testing."""
        with patch('cli.main.Config') as mock_config, \
             patch('cli.main.ChannelFactory') as mock_factory, \
             patch('cli.main.LLMClient') as mock_llm, \
             patch('cli.main.SearchEngine') as mock_search, \
             patch('cli.main.SupportAgent') as mock_agent, \
             patch('cli.main.FeedbackCollector') as mock_feedback, \
             patch('cli.main.PDFParser') as mock_pdf, \
             patch('cli.main.WebScraper') as mock_web, \
             patch('cli.main.IndexBuilder') as mock_index:
            
            # Configure mocks
            mock_config.from_env.return_value = MagicMock(
                vector_db_path="data/test_index",
                feedback_log_path="logs/test_feedback.log",
                llm_provider="ollama",
                llm_api_key="",
                channel="cli"
            )
            
            mock_input = MagicMock()
            mock_input.get_user_query.side_effect = ["test query", "quit"]
            mock_input.get_feedback.return_value = 5
            
            mock_output = MagicMock()
            
            mock_factory.create_channel.return_value = (mock_input, mock_output)
            
            mock_agent.return_value.handle_query.return_value = "Test response"
            
            mock_pdf.return_value.extract_text.return_value = "PDF content"
            mock_pdf.return_value.process_directory.return_value = [
                {'file_path': '/test/doc.pdf', 'text': 'PDF content'}
            ]
            
            mock_web.return_value.extract_content.return_value = {
                'content': 'Web content',
                'metadata': {'url': 'https://example.com'}
            }
            
            yield {
                'config': mock_config,
                'factory': mock_factory,
                'llm': mock_llm,
                'search': mock_search,
                'agent': mock_agent,
                'feedback': mock_feedback,
                'pdf': mock_pdf,
                'web': mock_web,
                'index': mock_index,
                'input': mock_input,
                'output': mock_output
            }
    
    def test_setup_and_run_workflow(self, mock_environment):
        """Test the complete workflow: setup resources and then run the agent."""
        runner = CliRunner()
        
        # Mock os.path methods
        with patch('os.path.isdir', return_value=False), \
             patch('os.path.exists', return_value=True):
            
            # Step 1: Run setup to ingest a PDF
            setup_result = runner.invoke(cli, ['setup'], input="y\n/test/doc.pdf\nn\nn\n")
            assert setup_result.exit_code == 0
            mock_environment['pdf'].return_value.extract_text.assert_called_once()
            mock_environment['index'].return_value.add_document.assert_called_once()
            
            # Step 2: Run the agent
            run_result = runner.invoke(cli, ['run'])
            assert run_result.exit_code == 0
            
            # Verify agent was initialized and used
            mock_environment['agent'].return_value.handle_query.assert_called_once_with("test query")
            mock_environment['output'].display_response.assert_called_once_with("Test response")
            mock_environment['feedback'].return_value.log_feedback.assert_called_once()
    
    def test_stats_after_usage(self, mock_environment):
        """Test the stats command after agent usage."""
        runner = CliRunner()
        
        # Mock feedback stats
        mock_environment['feedback'].return_value.get_feedback_stats.return_value = {
            'total_queries': 1,
            'rated_queries': 1,
            'average_rating': 5.0
        }
        
        # Run stats command
        result = runner.invoke(cli, ['stats'])
        
        # Verify command executed successfully
        assert result.exit_code == 0
        assert "Total Queries: 1" in result.output
        assert "Average Rating: 5.00" in result.output