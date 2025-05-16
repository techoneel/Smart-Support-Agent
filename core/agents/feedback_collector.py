import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

class FeedbackCollector:
    """Collector for user feedback and query logging."""
    
    def __init__(self, log_path: str):
        """Initialize the feedback collector.
        
        Args:
            log_path (str): Path to the feedback log file
        """
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    def log_feedback(
        self,
        query: str,
        response: str,
        rating: Optional[int],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log user feedback for a query-response pair.
        
        Args:
            query (str): The user's query
            response (str): The agent's response
            rating (Optional[int]): User rating (typically 1-5) or None if not provided
            metadata (Optional[Dict[str, Any]]): Additional metadata to log
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response,
            "rating": rating,
            **(metadata or {})
        }
        
        # Append to log file
        with open(self.log_path, 'a', encoding='utf-8') as f:
            json.dump(entry, f)
            f.write('\n')
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """Calculate statistics from the feedback log.
        
        Returns:
            Dict[str, Any]: Statistics like average rating, total queries, etc.
        """
        if not os.path.exists(self.log_path):
            return {
                "total_queries": 0,
                "rated_queries": 0,
                "average_rating": None
            }
        
        total_queries = 0
        rated_queries = 0
        total_rating = 0
        
        with open(self.log_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    total_queries += 1
                    if entry.get("rating") is not None:
                        rated_queries += 1
                        total_rating += entry["rating"]
        
        return {
            "total_queries": total_queries,
            "rated_queries": rated_queries,
            "average_rating": (total_rating / rated_queries) if rated_queries > 0 else None
        }