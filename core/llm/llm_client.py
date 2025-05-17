from typing import Dict, Any, Optional, List
import requests
import json
from langchain_core.language_models import BaseLLM
from langchain_core.callbacks import CallbackManagerForLLMRun

class LLMClient:
    """Client for interacting with various LLM providers."""
    
    def __init__(self, provider: str, api_key: str = "", model: Optional[str] = None):
        """Initialize the LLM client.
        
        Args:
            provider (str): The LLM provider ("together", "ollama", "openai", or "gemini")
            api_key (str): API key for the provider
            model (Optional[str]): Model name
            
        Raises:
            ValueError: If provider is not supported or configuration is invalid
        """
        provider = provider.lower().strip()
        if provider not in ["together", "ollama", "openai", "gemini"]:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                "Supported providers are: together, ollama, openai, gemini"
            )
            
        # Validate required configuration
        if provider in ["together", "openai", "gemini"] and not api_key:
            raise ValueError(f"{provider} requires an API key")
            
        self.provider = provider
        self.api_key = api_key
        self.model = model
        
        # Default models for each provider
        self.default_models = {
            "together": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "ollama": "llama2",
            "openai": "gpt-3.5-turbo",
            "gemini": "gemini-2.0-flash",
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
        elif self.provider == "gemini":
            return self._call_gemini(prompt, temperature, max_tokens)
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
            
        Raises:
            ValueError: If Ollama service is not running or model is not available
        """
        data = {
            "model": self.model or "llama2",
            "prompt": prompt,
            "temperature": temperature,
            "num_predict": max_tokens
        }
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=data,
                timeout=5  # Add timeout to fail fast if service is down
            )
            
            if response.status_code == 404:
                raise ValueError(f"Model '{self.model}' not found. Make sure to pull it first with 'ollama pull {self.model}'")
            elif response.status_code != 200:
                raise ValueError(f"API call failed: {response.text}")
            
            # Parse streaming response
            full_response = ""
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if "response" in chunk:
                        full_response += chunk["response"]
                    elif "error" in chunk:
                        raise ValueError(f"Ollama error: {chunk['error']}")
            
            return full_response
            
        except requests.exceptions.ConnectionError:
            raise ValueError(
                "Could not connect to Ollama service. Make sure Ollama is installed and running:\n"
                "1. Install Ollama from https://ollama.com/download\n"
                "2. Start the Ollama service\n"
                "3. Pull the model with: ollama pull llama2"
            )
        except requests.exceptions.Timeout:
            raise ValueError(
                "Connection to Ollama service timed out. Make sure Ollama is running and responsive"
            )
    
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
        
    def _call_gemini(self, prompt: str, temperature: float, max_tokens: int) -> str:
        """Call Google Gemini API.
        
        Args:
            prompt (str): The prompt to send
            temperature (float): Temperature for generation
            max_tokens (int): Maximum tokens to generate
            
        Returns:
            str: The generated response
            
        Raises:
            ValueError: If API key is invalid or missing
            Exception: If the API call fails for other reasons
        """
        # Validate API key first
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError(
                "Invalid Gemini API key. Please set a valid API key in your .env file:\n"
                "1. Get an API key from https://ai.google.dev/\n"
                "2. Set SSA_LLM_API_KEY=your_api_key_here in .env\n"
                "3. Or switch to Ollama by setting SSA_LLM_PROVIDER=ollama"
            )
            
        headers = {
            "Content-Type": "application/json"
        }
        
        # Use the model from config, but ensure it's a valid model name
        model = self.model
        
        # Gemini API endpoint
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        
        # Add API key as query parameter
        url += f"?key={self.api_key}"
        
        # Prepare the request data
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data
            )
            
            if response.status_code == 400:
                response_json = response.json()
                error_message = response_json.get("error", {}).get("message", "Unknown error")
                
                if "API key not valid" in error_message:
                    raise ValueError(
                        "Invalid Gemini API key. Please set a valid API key in your .env file:\n"
                        "1. Get an API key from https://ai.google.dev/\n"
                        "2. Set SSA_LLM_API_KEY=your_api_key_here in .env\n"
                        "3. Or switch to Ollama by setting SSA_LLM_PROVIDER=ollama"
                    )
                else:
                    raise Exception(f"Gemini API error: {error_message}")
            
            elif response.status_code == 429:
                response_json = response.json()
                error_message = response_json.get("error", {}).get("message", "Rate limit exceeded")
                
                # Extract retry delay if available
                retry_delay = "60 seconds"
                for detail in response_json.get("error", {}).get("details", []):
                    if "@type" in detail and "RetryInfo" in detail["@type"]:
                        if "retryDelay" in detail:
                            retry_delay = detail["retryDelay"]
                
                raise ValueError(
                    f"Gemini API rate limit exceeded. Please try again after {retry_delay}.\n"
                    "Options:\n"
                    "1. Wait and try again later\n"
                    "2. Switch to Ollama by setting SSA_LLM_PROVIDER=ollama in your .env file\n"
                    "3. Upgrade your Gemini API quota at https://ai.google.dev/"
                )
            
            elif response.status_code != 200:
                raise Exception(f"Gemini API call failed with status {response.status_code}: {response.text}")
            
            response_json = response.json()
            
            # Extract the generated text from the response
            if "candidates" in response_json and len(response_json["candidates"]) > 0:
                candidate = response_json["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        return parts[0]["text"]
            
            raise Exception("Failed to extract text from Gemini API response")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error when calling Gemini API: {str(e)}")
        except ValueError as e:
            # Re-raise ValueError for API key issues
            raise
        except Exception as e:
            raise Exception(f"Error calling Gemini API: {str(e)}")


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