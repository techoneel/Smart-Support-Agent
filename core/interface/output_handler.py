from abc import ABC, abstractmethod


class OutputHandler(ABC):
    """Abstract base class for all output channels."""
    
    @abstractmethod
    def display_response(self, response: str) -> None:
        """Display a response to the user.
        
        Args:
            response (str): The response to display
        """
        pass
    
    @abstractmethod
    def display_error(self, error: str) -> None:
        """Display an error message to the user.
        
        Args:
            error (str): The error message to display
        """
        pass