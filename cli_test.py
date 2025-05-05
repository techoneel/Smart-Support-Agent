#!/usr/bin/env python
import click
from config.settings import Config

@click.group()
def cli():
    """Smart Support Agent CLI"""
    pass

@cli.command()
def version():
    """Display the version"""
    # from config.settings import __version__    
    __version__ = "0.0.1"
    click.echo(f"Smart Support Agent v{__version__}")

@cli.command()
def config():
    """Display the current configuration"""
    cfg = Config.from_env()
    click.echo("Current configuration:")
    for key, value in cfg.to_dict().items():
        # Hide API key
        if key == "llm_api_key" and value:
            value = "********"
        click.echo(f"  {key}: {value}")

if __name__ == "__main__":
    cli()