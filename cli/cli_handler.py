import click
from typing import Optional
from core.interface.input_handler import InputHandler
from core.interface.output_handler import OutputHandler


class CLIInputHandler(InputHandler):
    """CLI implementation of the input handler."""
    
    def get_user_query(self) -> str:
        """Get a query from the user via CLI.
        
        Returns:
            str: The user's query
        """
        return click.prompt("Ask a question", type=str)
    
    def get_feedback(self, response: str) -> Optional[int]:
        """Get feedback on a response from the user via CLI.
        
        Args:
            response (str): The response to get feedback on
            
        Returns:
            Optional[int]: The user's rating or None if skipped
        """
        if click.confirm("Would you like to rate this response?", default=True):
            return click.prompt(
                "Rate this response (1-5)", 
                type=click.IntRange(1, 5)
            )
        return None


class CLIOutputHandler(OutputHandler):
    """CLI implementation of the output handler."""
    
    def display_response(self, response: str) -> None:
        """Display a response to the user via CLI.
        
        Args:
            response (str): The response to display
        """
        click.echo("\n" + "=" * 40)
        click.echo("Answer:")
        click.echo("-" * 40)
        click.echo(response)
        click.echo("=" * 40 + "\n")
    
    def display_error(self, error: str) -> None:
        """Display an error message to the user via CLI.
        
        Args:
            error (str): The error message to display
        """
        click.secho(f"Error: {error}", fg='red')