import pytest
from unittest.mock import Mock, patch
from core.agents.support_agent import SupportAgent
from core.llm.llm_client import LLMClient
from core.retriever.search_engine import SearchEngine

@pytest.fixture
def mock_retriever():
    retriever = Mock(spec=SearchEngine)
    retriever.search.return_value = ["Test document 1", "Test document 2"]
    return retriever

@pytest.fixture
def mock_llm_client():
    llm_client = Mock(spec=LLMClient)
    llm_client.generate.return_value = "Test response"
    return llm_client

@pytest.fixture
def support_agent(mock_retriever, mock_llm_client):
    return SupportAgent(mock_retriever, mock_llm_client)

class TestSupportAgent:
    def test_handle_query(self, support_agent, mock_retriever, mock_llm_client):
        # Arrange
        query = "test query"
        expected_docs = ["Test document 1", "Test document 2"]
        expected_response = "Test response"
        
        # Act
        response = support_agent.handle_query(query)
        
        # Assert
        mock_retriever.search.assert_called_once_with(query)
        mock_llm_client.generate.assert_called_once()
        assert response == expected_response
    
    def test_build_prompt(self, support_agent):
        # Arrange
        query = "test query"
        docs = ["Doc 1", "Doc 2"]
        
        # Act
        prompt = support_agent._build_prompt(query, docs)
        
        # Assert
        assert "Doc 1" in prompt
        assert "Doc 2" in prompt
        assert query in prompt
        
    def test_build_prompt_no_docs(self, support_agent):
        # Arrange
        query = "test query"
        docs = []
        
        # Act
        prompt = support_agent._build_prompt(query, docs)
        
        # Assert
        assert "No relevant documents found" in prompt
        assert query in prompt
