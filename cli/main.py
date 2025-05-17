#!/usr/bin/env python
import click
from typing import Optional, List
import os
import traceback
import json
import numpy as np
import faiss

from config.settings import Config
from factory.channel_factory import ChannelFactory
from core.llm.llm_client import LLMClient
from core.retriever.search_engine import SearchEngine
from core.agents.support_agent import SupportAgent
from core.agents.feedback_collector import FeedbackCollector
from core.ingestor.pdf_parser import PDFParser
from core.ingestor.web_scraper import WebScraper
from core.retriever.index_builder import IndexBuilder

# Custom JSON encoder for NumPy arrays
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

@click.group()
def cli():
    """Smart Support Agent CLI"""
    pass

@cli.command()
@click.option('--config-path', type=str, help='Path to config file')
@click.option('--provider', type=str, help='Override LLM provider (ollama, gemini, openai, together)')
@click.option('--model', type=str, help='Override LLM model')
@click.option('--api-key', type=str, help='Override API key for cloud providers')
def run(config_path: Optional[str], provider: Optional[str], model: Optional[str], api_key: Optional[str]):
    """Run the support agent in interactive mode."""
    try:
        # Load configuration
        if config_path and os.path.exists(config_path):
            config = Config.from_file(config_path)
        else:
            config = Config.from_env()
            
        # Override configuration with command-line options if provided
        if provider:
            config.llm_provider = provider
        if model:
            config.llm_model = model
        if api_key:
            config.llm_api_key = api_key
        
        # Initialize components
        input_handler, output_handler = ChannelFactory.create_channel(config.channel)
        
        # Debug information
        click.echo(f"Using LLM provider: '{config.llm_provider}'")
        click.echo(f"Using model: '{config.llm_model}'")
        
        # Initialize core components
        try:
            llm_client = LLMClient(config.llm_provider, config.llm_api_key, config.llm_model)
            retriever = SearchEngine(config.vector_db_path or "data/faiss_index")
            
            # Create agent and feedback collector
            agent = SupportAgent(retriever, llm_client)
            feedback_collector = FeedbackCollector(config.feedback_log_path)
            
            click.echo("Smart Support Agent initialized. Type 'quit' to exit.")
            
            # Main interaction loop
            while True:
                try:
                    # Get user query
                    query = input_handler.get_user_query()
                    if query.lower() == "quit":
                        break
                    
                    # Process query
                    response = agent.handle_query(query)
                    
                    # Display response
                    output_handler.display_response(response)
                    
                    # Collect feedback
                    rating = input_handler.get_feedback(response)
                    feedback_collector.log_feedback(query, response, rating)
                    
                except Exception as e:
                    output_handler.display_error(str(e))
        except ValueError as e:
            error_msg = str(e)
            if "Could not connect to Ollama service" in error_msg or "Connection to Ollama service timed out" in error_msg:
                click.secho("Error: Ollama service is not running or not responding.", fg='red')
                click.echo("1. Install Ollama from https://ollama.com/download")
                click.echo("2. Start the Ollama service")
                click.echo("3. Pull the model with: ollama pull llama2")
                
                # Offer to switch to a cloud provider
                if click.confirm("Would you like to switch to Gemini API instead?", default=False):
                    api_key = click.prompt("Enter your Gemini API key", type=str)
                    if api_key:
                        # Update .env file
                        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
                        with open(env_path, 'r') as f:
                            env_content = f.read()
                        
                        # Replace provider and API key
                        env_content = env_content.replace('SSA_LLM_PROVIDER=ollama', 'SSA_LLM_PROVIDER=gemini')
                        env_content = env_content.replace('SSA_LLM_API_KEY=', f'SSA_LLM_API_KEY={api_key}')
                        env_content = env_content.replace('SSA_LLM_MODEL=llama2', 'SSA_LLM_MODEL=gemini-2.0-flash')
                        
                        with open(env_path, 'w') as f:
                            f.write(env_content)
                        
                        click.echo("Configuration updated. Please run the command again.")
                    else:
                        click.echo("No API key provided. Keeping Ollama configuration.")
            elif "Invalid Gemini API key" in error_msg:
                click.secho("Error: Invalid or missing Gemini API key.", fg='red')
                click.echo("1. Get an API key from https://ai.google.dev/")
                click.echo("2. Update your .env file with: SSA_LLM_API_KEY=your_api_key_here")
                click.echo("3. Or switch to Ollama by setting SSA_LLM_PROVIDER=ollama in your .env file")
            elif "Gemini API rate limit exceeded" in error_msg:
                click.secho("Error: Gemini API rate limit exceeded.", fg='red')
                click.echo("1. Wait and try again later")
                click.echo("2. Switch to Ollama by setting SSA_LLM_PROVIDER=ollama in your .env file")
                click.echo("3. Upgrade your Gemini API quota at https://ai.google.dev/")
            else:
                click.secho(f"Error: {error_msg}", fg='red')
                
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')

@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode with detailed error messages')
@click.option('--no-js', is_flag=True, help='Disable JavaScript rendering for web scraping')
def setup(debug: bool, no_js: bool):
    """Setup the agent by ingesting resources like PDFs and web pages."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Initialize components
        pdf_parser = PDFParser()
        web_scraper = WebScraper(session=requests.Session() if no_js else None)
        index_builder = IndexBuilder(config.vector_db_path or "data/faiss_index")
        
        click.echo("Smart Support Agent Setup")
        click.echo("========================")
        
        # Ask for PDF resources
        if click.confirm("Do you want to add PDF documents?", default=True):
            while True:
                pdf_path = click.prompt("Enter path to PDF file or directory", type=str)
                
                try:
                    if os.path.isdir(pdf_path):
                        click.echo(f"Processing directory: {pdf_path}")
                        documents = pdf_parser.process_directory(pdf_path)
                        click.echo(f"Found {len(documents)} PDF documents")
                        
                        for doc in documents:
                            click.echo(f"Adding: {doc['file_path']}")
                            index_builder.add_document(doc['text'])
                    else:
                        click.echo(f"Processing file: {pdf_path}")
                        try:
                            # Verify file exists and is readable
                            if not os.path.exists(pdf_path):
                                click.secho(f"Error: File not found: {pdf_path}", fg='red')
                                continue
                                
                            # Try to open the file to check if it's accessible
                            try:
                                with open(pdf_path, 'rb') as f:
                                    # Just check if we can read a bit of data
                                    f.read(10)
                            except Exception as access_error:
                                click.secho(f"Error: Cannot access file: {str(access_error)}", fg='red')
                                continue
                                
                            # Extract text from PDF
                            text = pdf_parser.extract_text(pdf_path)
                            
                            # Check if we got any text
                            if not text or text == "No extractable text found in PDF.":
                                click.secho("Warning: No text could be extracted from the PDF.", fg='yellow')
                                if click.confirm("Do you still want to add this document?", default=False):
                                    index_builder.add_document(text or "Empty document")
                                    click.echo("Document added with empty content.")
                                continue
                                
                            # Add document to index
                            index_builder.add_document(text)
                            click.echo("Document added successfully")
                            
                        except ValueError as pdf_error:
                            error_msg = str(pdf_error)
                            click.secho(f"Error processing PDF: {error_msg}", fg='red')
                            
                            # Offer suggestions based on error
                            if "encrypted" in error_msg.lower():
                                click.echo("This PDF is password-protected. Please provide an unencrypted PDF.")
                            elif "not a valid pdf" in error_msg.lower():
                                click.echo("The file doesn't appear to be a valid PDF. Please check the file format.")
                            elif "no extractable text" in error_msg.lower():
                                click.echo("This PDF doesn't contain extractable text. It may be scanned or image-based.")
                                click.echo("Consider using OCR software to convert it to a text-based PDF first.")
                            
                            # Show detailed error in debug mode
                            if debug:
                                click.echo("\nDetailed error information:")
                                click.echo(traceback.format_exc())
                                
                except Exception as e:
                    click.secho(f"Error processing PDF: {str(e)}", fg='red')
                    # Show detailed error in debug mode
                    if debug:
                        click.echo("\nDetailed error information:")
                        click.echo(traceback.format_exc())
                
                if not click.confirm("Add another PDF?", default=False):
                    break
        
        # Ask for web resources
        if click.confirm("Do you want to add web pages?", default=True):
            while True:
                url = click.prompt("Enter URL to scrape", type=str)
                max_pages = click.prompt("Maximum pages to crawl (1 for single page)", 
                                        default=1, type=int)
                
                try:
                    click.echo(f"Scraping URL: {url} (this may take a moment)...")
                    if max_pages > 1:
                        click.echo(f"Crawling site: {url} (max {max_pages} pages)")
                        results = web_scraper.crawl_site(url, max_pages=max_pages)
                        click.echo(f"Scraped {len(results)} pages")
                        
                        for i, result in enumerate(results):
                            click.echo(f"Adding page {i+1}: {result['metadata']['url']}")
                            if result['content'].strip():
                                index_builder.add_document(result['content'])
                                click.echo(f"Added content from {result['metadata']['url']}")
                            else:
                                click.secho(f"Warning: No content extracted from {result['metadata']['url']}", fg='yellow')
                    else:
                        click.echo(f"Scraping page: {url}")
                        result = web_scraper.extract_content(url)
                        if result['content'].strip():
                            index_builder.add_document(result['content'])
                            click.echo("Page added successfully")
                        else:
                            click.secho("Warning: No content extracted from page", fg='yellow')
                            if click.confirm("Do you want to try again with JavaScript disabled?", default=True):
                                simple_scraper = WebScraper(session=requests.Session())
                                result = simple_scraper.extract_content(url)
                                if result['content'].strip():
                                    index_builder.add_document(result['content'])
                                    click.echo("Page added successfully with simple scraper")
                                else:
                                    click.secho("Still no content extracted. Skipping page.", fg='red')
                except Exception as e:
                    click.secho(f"Error scraping URL: {str(e)}", fg='red')
                    click.echo("Try using a different URL or check your internet connection.")
                    # Show detailed error in debug mode
                    if debug:
                        click.echo("\nDetailed error information:")
                        click.echo(traceback.format_exc())
                    
                    # Offer to try with simple scraper
                    if not no_js and "Chromium" in str(e):
                        if click.confirm("Do you want to try again with JavaScript disabled?", default=True):
                            try:
                                click.echo("Trying with simple scraper (no JavaScript rendering)...")
                                simple_scraper = WebScraper(session=requests.Session())
                                result = simple_scraper.extract_content(url)
                                if result['content'].strip():
                                    index_builder.add_document(result['content'])
                                    click.echo("Page added successfully with simple scraper")
                                else:
                                    click.secho("No content extracted. Skipping page.", fg='red')
                            except Exception as simple_error:
                                click.secho(f"Error with simple scraper: {str(simple_error)}", fg='red')
                
                if not click.confirm("Add another URL?", default=False):
                    break
        
        click.echo("\nSetup complete! Your knowledge base is ready.")
        click.echo("Run 'python cli/main.py run' to start the agent.")
        
    except Exception as e:
        click.secho(f"Error during setup: {str(e)}", fg='red')
        # Show detailed error in debug mode
        if debug:
            click.echo("\nDetailed error information:")
            click.echo(traceback.format_exc())

@cli.command()
@click.option('--export', type=str, help='Export index to a file (JSON format)')
@click.option('--limit', type=int, default=10, help='Limit the number of vectors to display')
@click.option('--index-path', type=str, help='Path to the FAISS index file')
def view_index(export: Optional[str], limit: int, index_path: Optional[str]):
    """View and export the FAISS index for visualization."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Get index path
        index_path = index_path or config.vector_db_path or "data/faiss_index"
        
        if not os.path.exists(index_path):
            click.secho(f"Error: Index file not found at {index_path}", fg='red')
            return
        
        # Load the index
        click.echo(f"Loading index from {index_path}...")
        index = faiss.read_index(index_path)
        
        # Display index information
        click.echo("\nFAISS Index Information:")
        click.echo("-" * 40)
        click.echo(f"Index type: {type(index).__name__}")
        click.echo(f"Dimension: {index.d}")
        click.echo(f"Total vectors: {index.ntotal}")
        click.echo(f"Is trained: {index.is_trained}")
        click.echo("-" * 40)
        
        # If the index is empty, there's nothing more to show
        if index.ntotal == 0:
            click.echo("Index is empty. No vectors to display.")
            return
        
        # Get some vectors from the index if possible
        if hasattr(index, 'reconstruct'):
            click.echo(f"\nSample vectors (showing up to {limit}):")
            for i in range(min(limit, index.ntotal)):
                try:
                    vector = index.reconstruct(i)
                    # Show just the first few dimensions to avoid cluttering the output
                    preview = ', '.join(f"{x:.4f}" for x in vector[:5])
                    click.echo(f"Vector {i}: [{preview}{'...' if len(vector) > 5 else ''}]")
                except Exception as e:
                    click.echo(f"Could not reconstruct vector {i}: {str(e)}")
        else:
            click.echo("\nThis index type doesn't support vector reconstruction.")
        
        # Export the index if requested
        if export:
            try:
                # Create a dictionary with index information
                index_data = {
                    "type": type(index).__name__,
                    "dimension": int(index.d),
                    "total_vectors": int(index.ntotal),
                    "is_trained": bool(index.is_trained),
                    "vectors": []
                }
                
                # Add vectors if possible
                if hasattr(index, 'reconstruct'):
                    for i in range(min(limit, index.ntotal)):
                        try:
                            vector = index.reconstruct(i)
                            index_data["vectors"].append({
                                "id": i,
                                "vector": vector
                            })
                        except Exception:
                            pass
                
                # Write to file
                with open(export, 'w') as f:
                    json.dump(index_data, f, cls=NumpyEncoder, indent=2)
                
                click.echo(f"\nIndex exported to {export}")
                click.echo("You can visualize this data using tools like:")
                click.echo("- TensorBoard Projector: https://projector.tensorflow.org/")
                click.echo("- UMAP Explorer: https://umap-learn.readthedocs.io/")
                click.echo("- t-SNE Viewer: https://github.com/distillpub/post--misread-tsne")
            except Exception as e:
                click.secho(f"Error exporting index: {str(e)}", fg='red')
        
    except Exception as e:
        click.secho(f"Error viewing index: {str(e)}", fg='red')

@cli.command()
def stats():
    """Display usage statistics."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Initialize feedback collector
        feedback_collector = FeedbackCollector(config.feedback_log_path)
        
        # Get statistics
        stats = feedback_collector.get_feedback_stats()
        
        # Display statistics
        click.echo("\nUsage Statistics:")
        click.echo("-" * 40)
        click.echo(f"Total Queries: {stats['total_queries']}")
        click.echo(f"Rated Queries: {stats['rated_queries']}")
        if stats['average_rating'] is not None:
            click.echo(f"Average Rating: {stats['average_rating']:.2f}")
        else:
            click.echo("Average Rating: No ratings yet")
        click.echo("-" * 40)
        
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')

if __name__ == "__main__":
    cli()