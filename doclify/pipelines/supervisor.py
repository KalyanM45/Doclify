import click
import shutil
from rich.console import Console
from dotenv import load_dotenv

from doclify.components.init import init_project
from doclify import __version__

console = Console()

# Load environment variables from a .env file if it exists in the current directory
load_dotenv()

@click.group()
@click.version_option(version=__version__)
def cli():
    """
    Doclify: AI-powered project documentation generator.
    
    Automatically generate, update, and manage your project's 
    README and codebase documentation using LLMs.
    """
    pass

@cli.command()
def init():
    """Initialize a new Doclify project and create doclify.yaml."""
    init_project()

@cli.group(name="set")
def set_group():
    """Set configuration settings for Doclify."""
    pass

@set_group.command("default")
@click.argument("model")
def set_default(model):
    """Set the default LLM model in doclify.yaml"""
    from doclify.components.config import update_config
    update_config(model=model)

@cli.command()
@click.option('--model', help='Override the LLM model.')
@click.option('--provider', help='Override the LLM provider.')
def run(model, provider):
    """Run the documentation generation pipeline for the project."""
    from doclify.components.run import run_docs
    run_docs(model=model, provider=provider)

@cli.command()
@click.argument('path', type=click.Path(exists=True), required=True)
@click.option('--model', help='Override the LLM model.')
@click.option('--provider', help='Override the LLM provider.')
def update(path, model, provider):
    """Update documentation for a specific file or all files (use '.')."""
    from doclify.components.update import update_docs
    update_docs(path, model=model, provider=provider)

@cli.command()
def models():
    """List all available models from Groq."""
    from doclify.components.models import list_models
    list_models()