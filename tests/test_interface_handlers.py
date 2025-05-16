import pytest
from unittest.mock import Mock
from core.interface.input_handler import InputHandler
from core.interface.output_handler import OutputHandler

class MockInputHandler(InputHandler):
    def get_user_query(self) -> str:
        return "test query"
        
    def get_feedback(self, response: str) -> int:
        return 5

class MockOutputHandler(OutputHandler):
    def display_response(self, response: str) -> None:
        pass
        
    def display_error(self, error: str) -> None:
        pass

class TestInputHandler:
    def test_input_handler_interface(self):
        # Arrange
        handler = MockInputHandler()
        
        # Act & Assert
        assert handler.get_user_query() == "test query"
        assert handler.get_feedback("test response") == 5
        
    def test_input_handler_is_abstract(self):
        # Act & Assert
        with pytest.raises(TypeError):
            InputHandler()

class TestOutputHandler:
    def test_output_handler_interface(self):
        # Arrange
        handler = MockOutputHandler()
        
        # Act & Assert - should not raise
        handler.display_response("test response")
        handler.display_error("test error")
        
    def test_output_handler_is_abstract(self):
        # Act & Assert
        with pytest.raises(TypeError):
            OutputHandler()

class TestBaseInputHandler:
    def test_get_user_query_not_implemented(self):
        # Arrange
        class ConcreteInput(InputHandler):
            pass  # Don't implement abstract methods
        
        # Act & Assert
        with pytest.raises(TypeError):
            ConcreteInput()
    
    def test_get_feedback_not_implemented(self):
        # Arrange
        class ConcreteInput(InputHandler):
            def get_user_query(self) -> str:
                return "query"
        
        # Act & Assert
        with pytest.raises(TypeError):
            ConcreteInput()

    def test_input_handler_implementation(self):
        # Arrange
        class ConcreteInput(InputHandler):
            def get_user_query(self) -> str:
                return "test query"
            
            def get_feedback(self, response: str) -> int:
                return 5 if "good" in response else 1
        
        # Act
        handler = ConcreteInput()
        query = handler.get_user_query()
        feedback_good = handler.get_feedback("good response")
        feedback_bad = handler.get_feedback("bad response")
        
        # Assert
        assert query == "test query"
        assert feedback_good == 5
        assert feedback_bad == 1

class TestBaseOutputHandler:
    def test_display_response_not_implemented(self):
        # Arrange
        class ConcreteOutput(OutputHandler):
            pass  # Don't implement abstract methods
        
        # Act & Assert
        with pytest.raises(TypeError):
            ConcreteOutput()
    
    def test_display_error_not_implemented(self):
        # Arrange
        class ConcreteOutput(OutputHandler):
            def display_response(self, response: str) -> None:
                pass
        
        # Act & Assert
        with pytest.raises(TypeError):
            ConcreteOutput()

    def test_output_handler_implementation(self):
        # Arrange
        class ConcreteOutput(OutputHandler):
            def __init__(self):
                self.responses = []
                self.errors = []
            
            def display_response(self, response: str) -> None:
                self.responses.append(response)
            
            def display_error(self, error: str) -> None:
                self.errors.append(error)
        
        # Act
        handler = ConcreteOutput()
        handler.display_response("test response")
        handler.display_error("test error")
        
        # Assert
        assert handler.responses == ["test response"]
        assert handler.errors == ["test error"]
