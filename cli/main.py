#!/usr/bin/env python
import click
from typing import Optional, List
import os

from config.settings import Config
from factory.channel_factory import ChannelFactory
from core.llm.llm_client import LLMClient
from core.retriever.search_engine import SearchEngine
from core.agents.support_agent import SupportAgent
from core.agents.feedback_collector import FeedbackCollector
from core.ingestor.pdf_parser import PDFParser
from core.ingestor.web_scraper import WebScraper
from core.retriever.index_builder import IndexBuilder

@click.group()
def cli():
    """Smart Support Agent CLI"""
    pass

@cli.command()
@click.option('--config-path', type=str, help='Path to config file')
def run(config_path: Optional[str]):
    """Run the support agent in interactive mode."""
    try:
        # Load configuration
        if config_path and os.path.exists(config_path):
            config = Config.from_file(config_path)
        else:
            config = Config.from_env()
        
        # Initialize components
        input_handler, output_handler = ChannelFactory.create_channel(config.channel)
        
        # Initialize core components
        llm_client = LLMClient(config.llm_provider, config.llm_api_key)
        retriever = SearchEngine(config.vector_db_path)
        
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
                
    except Exception as e:
        click.secho(f"Error: {str(e)}", fg='red')

@cli.command()
def setup():
    """Setup the agent by ingesting resources like PDFs and web pages."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Initialize components
        pdf_parser = PDFParser()
        web_scraper = WebScraper()
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
                        text = pdf_parser.extract_text(pdf_path)
                        index_builder.add_document(text)
                        click.echo("Document added successfully")
                except Exception as e:
                    click.secho(f"Error processing PDF: {str(e)}", fg='red')
                
                if not click.confirm("Add another PDF?", default=False):
                    break
        
        # Ask for web resources
        if click.confirm("Do you want to add web pages?", default=True):
            while True:
                url = click.prompt("Enter URL to scrape", type=str)
                max_pages = click.prompt("Maximum pages to crawl (1 for single page)", 
                                        default=1, type=int)
                
                try:
                    if max_pages > 1:
                        click.echo(f"Crawling site: {url} (max {max_pages} pages)")
                        results = web_scraper.crawl_site(url, max_pages=max_pages)
                        click.echo(f"Scraped {len(results)} pages")
                        
                        for i, result in enumerate(results):
                            click.echo(f"Adding page {i+1}: {result['metadata']['url']}")
                            index_builder.add_document(result['content'])
                    else:
                        click.echo(f"Scraping page: {url}")
                        result = web_scraper.extract_content(url)
                        index_builder.add_document(result['content'])
                        click.echo("Page added successfully")
                except Exception as e:
                    click.secho(f"Error scraping URL: {str(e)}", fg='red')
                
                if not click.confirm("Add another URL?", default=False):
                    break
        
        click.echo("\nSetup complete! Your knowledge base is ready.")
        click.echo("Run 'python cli/main.py run' to start the agent.")
        
    except Exception as e:
        click.secho(f"Error during setup: {str(e)}", fg='red')

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
