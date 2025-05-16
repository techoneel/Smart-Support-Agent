from typing import Optional, List
from ..retriever.search_engine import SearchEngine
from ..llm.llm_client import LLMClient

class SupportAgent:
    """Core agent logic for handling user queries."""
    
    def __init__(self, retriever: SearchEngine, llm_client: LLMClient):
        """Initialize the support agent.
        
        Args:
            retriever (SearchEngine): The search engine for document retrieval
            llm_client (LLMClient): The LLM client for response generation
        """
        self.retriever = retriever
        self.llm_client = llm_client
    
    def handle_query(self, query: str) -> str:
        """Handle a user query by retrieving relevant documents and generating a response.
        
        Args:
            query (str): The user's query
            
        Returns:
            str: The generated response
        """
        # 1. Retrieve relevant documents
        docs = self.retriever.search(query)
        
        # 2. Generate response using LLM
        prompt = self._build_prompt(query, docs)
        response = self.llm_client.generate(prompt)
        
        return response
    
    def _build_prompt(self, query: str, docs: List[str]) -> str:
        """Build a prompt for the LLM using the query and retrieved documents.
        
        Args:
            query (str): The user's query
            docs (List[str]): Retrieved relevant documents
            
        Returns:
            str: The constructed prompt
        """
        # Basic prompt template
        context = "\n---\n".join(docs) if docs else "No relevant documents found."
        
        prompt = f"""Given the following context:
---
{context}
---

Answer the user's question:
{query}

If the context doesn't contain relevant information, say that you cannot answer based on the available information.
Answer:"""
        
        return prompt