import pytest
from factory.channel_factory import ChannelFactory
from cli.cli_handler import CLIInputHandler, CLIOutputHandler

class TestChannelFactory:
    def test_create_cli_channel(self):
        # Act
        input_handler, output_handler = ChannelFactory.create_channel("cli")
        
        # Assert
        assert isinstance(input_handler, CLIInputHandler)
        assert isinstance(output_handler, CLIOutputHandler)
    
    def test_create_unknown_channel(self):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            ChannelFactory.create_channel("unknown")
        assert "Unknown channel type" in str(exc_info.value)
