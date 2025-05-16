from typing import Tuple
from core.interface.input_handler import InputHandler
from core.interface.output_handler import OutputHandler
from cli.cli_handler import CLIInputHandler, CLIOutputHandler


class ChannelFactory:
    """Factory for creating input/output channel handlers."""
    
    @staticmethod
    def create_channel(channel_type: str) -> Tuple[InputHandler, OutputHandler]:
        """Create input and output handlers for a channel.
        
        Args:
            channel_type (str): The channel type ("cli", "whatsapp", "web")
            
        Returns:
            Tuple[InputHandler, OutputHandler]: Input and output handlers
            
        Raises:
            ValueError: If the channel type is unknown
        """
        if channel_type == "cli":
            return CLIInputHandler(), CLIOutputHandler()
        # Future implementations would go here:
        # elif channel_type == "whatsapp":
        #     return WhatsAppInputHandler(), WhatsAppOutputHandler()
        # elif channel_type == "web":
        #     return WebInputHandler(), WebOutputHandler()
        else:
            raise ValueError(f"Unknown channel type: {channel_type}")