import pytest
import os
import json
from datetime import datetime
from core.agents.feedback_collector import FeedbackCollector

@pytest.fixture
def temp_log_file(tmp_path):
    return str(tmp_path / "test_feedback.log")

@pytest.fixture
def feedback_collector(temp_log_file):
    return FeedbackCollector(temp_log_file)

class TestFeedbackCollector:
    def test_log_feedback(self, feedback_collector, temp_log_file):
        # Arrange
        query = "test query"
        response = "test response"
        rating = 5
        
        # Act
        feedback_collector.log_feedback(query, response, rating)
        
        # Assert
        with open(temp_log_file, 'r') as f:
            log_entry = json.loads(f.readline())
            assert log_entry["query"] == query
            assert log_entry["response"] == response
            assert log_entry["rating"] == rating
            assert "timestamp" in log_entry
    
    def test_log_feedback_with_metadata(self, feedback_collector, temp_log_file):
        # Arrange
        metadata = {"user_id": "123", "session_id": "abc"}
        
        # Act
        feedback_collector.log_feedback(
            "query",
            "response",
            4,
            metadata=metadata
        )
        
        # Assert
        with open(temp_log_file, 'r') as f:
            log_entry = json.loads(f.readline())
            assert log_entry["user_id"] == "123"
            assert log_entry["session_id"] == "abc"
    
    def test_get_feedback_stats_empty(self, feedback_collector):
        # Act
        stats = feedback_collector.get_feedback_stats()
        
        # Assert
        assert stats["total_queries"] == 0
        assert stats["rated_queries"] == 0
        assert stats["average_rating"] is None
    
    def test_get_feedback_stats(self, feedback_collector):
        # Arrange
        feedback_collector.log_feedback("q1", "r1", 4)
        feedback_collector.log_feedback("q2", "r2", 2)
        feedback_collector.log_feedback("q3", "r3", None)
        
        # Act
        stats = feedback_collector.get_feedback_stats()
        
        # Assert
        assert stats["total_queries"] == 3
        assert stats["rated_queries"] == 2
        assert stats["average_rating"] == 3.0  # (4 + 2) / 2
