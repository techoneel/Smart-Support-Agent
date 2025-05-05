from typing import Dict, Any, Optional, List
import requests
import json
import os
from langchain_core.language_models import BaseLLM
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import GenerationChunk

class LLMClient:
    """Client for interacting with various LLM providers."""
    
    def __init__(self, provider: str, api_key: str = "", model: Optional[str] = None):
        """Initialize the LLM client.
        
        Args:
            provider (str): The LLM provider ("together", "ollama", etc.)
            api_key (str): API key for the provider
            model (Optional[str]): Model name
        """
        self.provider = provider.lower()
        self.api_key = api_key
        self.model = model
        
        # Default models for each provider
        self.default_models = {
            "together": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "ollama": "llama2",
            "openai": "gpt-3.5-turbo",
        }
        
        # Select model if not provided
        if not self.model:
            self.model = self.default_models.get(self.provider, "")
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt (str): The prompt to send to the LLM
            temperature (float): Temperature for generation
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
        """
        if self.provider == "together":
            return self._call_together_ai(prompt, temperature, max_tokens)
        elif self.provider == "ollama":
            return self._call_ollama(prompt, temperature, max_tokens)
        elif self.provider == "openai":
            return self._call_openai(prompt, temperature, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
    
    def _call_together_ai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Together.ai API.
        
        Args:
            prompt (str): The prompt to send
            temperature (float): Temperature for generation
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://api.together.xyz/v1/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.text}")
        
        return response.json()["choices"][0]["text"]
    
    def _call_ollama(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Ollama API.
        
        Args:
            prompt (str): The prompt to send
            temperature (float): Temperature for generation
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
        """
        data = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.text}")
        
        # Parse streaming response
        full_response = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line.decode('utf-8'))
                if "response" in chunk:
                    full_response += chunk["response"]
        
        return full_response
    
    def _call_openai(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call OpenAI API.
        
        Args:
            prompt (str): The prompt to send
            temperature (float): Temperature for generation
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            raise Exception(f"API call failed: {response.text}")
        
        return response.json()["choices"][0]["message"]["content"]


# LangChain-compatible wrapper for the LLMClient
class LLMClientWrapper(BaseLLM):
    """LangChain wrapper for LLMClient."""
    
    def __init__(self, provider: str, api_key: str = "", model: Optional[str] = None):
        """Initialize the LLM client wrapper.
        
        Args:
            provider (str): The LLM provider
            api_key (str): API key for the provider
            model (Optional[str]): Model name
        """
        super().__init__()
        self.llm_client = LLMClient(provider, api_key, model)
    
    @property
    def _llm_type(self) -> str:
        """Return the LLM type.
        
        Returns:
            str: The LLM type
        """
        return f"{self.llm_client.provider}-{self.llm_client.model}"
    
    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Any:
        """Generate responses for the prompts.
        
        Args:
            prompts (List[str]): The prompts to generate responses for
            stop (Optional[List[str]]): Stop sequences
            run_manager (Optional[CallbackManagerForLLMRun]): Callback manager
            **kwargs (Any): Additional arguments
            
        Returns:
            Any: LLMResult with generations
        """
        from langchain_core.outputs import LLMResult, Generation
        
        generations = []
        for prompt in prompts:
            text = self.llm_client.generate(
                prompt, 
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 1024)
            )
            generations.append([Generation(text=text)])
            
        return LLMResult(generations=generations)