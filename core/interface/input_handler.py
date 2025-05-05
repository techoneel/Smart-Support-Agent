from abc import ABC, abstractmethod
from typing import Optional


class InputHandler(ABC):
    """Abstract base class for all input channels."""
    
    @abstractmethod
    def get_user_query(self) -> str:
        """Get a query from the user.
        
        Returns:
            str: The user's query
        """
        pass
    
    @abstractmethod
    def get_feedback(self, response: str) -> Optional[int]:
        """Get feedback on a response from the user.
        
        Args:
            response (str): The response to get feedback on
            
        Returns:
            Optional[int]: The user's rating (typically 1-5) or None if no feedback
        """
        pass