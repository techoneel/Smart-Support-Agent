#!/usr/bin/env python
import click
from core.llm.llm_client import LLMClient
from config.settings import Config

@click.command()
@click.option('--prompt', default="What is Python?", help='Prompt to send to the LLM')
@click.option('--provider', default=None, help='LLM provider (ollama, together, openai)')
@click.option('--model', default=None, help='Model to use')
def test_llm(prompt, provider, model):
    """Test the LLM client with a simple prompt."""
    # Load configuration
    config = Config.from_env()
    
    # Override with command line arguments if provided
    provider = provider or config.llm_provider
    model = model or config.llm_model
    api_key = config.llm_api_key
    
    click.echo(f"Testing LLM with provider: {provider}, model: {model}")
    click.echo(f"Prompt: {prompt}")
    
    try:
        # Initialize LLM client
        llm_client = LLMClient(provider, api_key, model)
        
        # Generate response
        click.echo("\nGenerating response...")
        response = llm_client.generate(prompt)
        
        # Display response
        click.echo("\nResponse:")
        click.echo("-" * 40)
        click.echo(response)
        click.echo("-" * 40)
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')
        
if __name__ == "__main__":
    test_llm()