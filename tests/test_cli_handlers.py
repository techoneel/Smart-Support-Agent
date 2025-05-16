import pytest
from unittest.mock import patch
from cli.cli_handler import CLIInputHandler, CLIOutputHandler

@pytest.fixture
def cli_input():
    return CLIInputHandler()

@pytest.fixture
def cli_output():
    return CLIOutputHandler()

class TestCLIHandlers:
    @patch('click.prompt')
    def test_get_user_query(self, mock_prompt, cli_input):
        # Arrange
        expected_query = "test query"
        mock_prompt.return_value = expected_query
        
        # Act
        query = cli_input.get_user_query()
        
        # Assert
        assert query == expected_query
        mock_prompt.assert_called_once_with("Ask a question", type=str)
    
    @patch('click.prompt')
    @patch('click.confirm')
    def test_get_feedback_with_rating(self, mock_confirm, mock_prompt, cli_input):
        # Arrange
        mock_confirm.return_value = True
        mock_prompt.return_value = 4
        
        # Act
        rating = cli_input.get_feedback("test response")
        
        # Assert
        assert rating == 4
        mock_confirm.assert_called_once()
        mock_prompt.assert_called_once()
    
    @patch('click.confirm')
    def test_get_feedback_skipped(self, mock_confirm, cli_input):
        # Arrange
        mock_confirm.return_value = False
        
        # Act
        rating = cli_input.get_feedback("test response")
        
        # Assert
        assert rating is None
        mock_confirm.assert_called_once()
    
    @patch('click.echo')
    def test_display_response(self, mock_echo, cli_output):
        # Arrange
        response = "test response"
        
        # Act
        cli_output.display_response(response)
        
        # Assert
        mock_echo.assert_any_call("\n" + "=" * 40)
        mock_echo.assert_any_call("Answer:")
        mock_echo.assert_any_call("-" * 40)
        mock_echo.assert_any_call(response)
    
    @patch('click.secho')
    def test_display_error(self, mock_secho, cli_output):
        # Arrange
        error = "test error"
        
        # Act
        cli_output.display_error(error)
        
        # Assert
        mock_secho.assert_called_once_with(f"Error: {error}", fg='red')
