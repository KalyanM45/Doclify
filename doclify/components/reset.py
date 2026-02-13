import os
from pathlib import Path
from rich.console import Console
from doclify.utils.file_utils import CACHE_FILE
from doclify.utils.logger import get_logger

# Initialize production-level logger and clean console
logger = get_logger(__name__)
console = Console()

def reset_project():
    """
    Clears the Doclify cache.
    """
    logger.info("Initiating project reset (cache clearing).")
    
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
            logger.info("Cache file deleted successfully.")
            console.print("[bold green]Success:[/bold green] [white]Cache cleared successfully.[/white]")
        else:
            logger.info("No cache file found to delete.")
            console.print("[bold yellow]⚠ Info:[/bold yellow] [white]No cache found. Nothing to reset.[/white]")
            
    except Exception as e:
        logger.error(f"Failed to reset project: {str(e)}", exc_info=True)
        console.print(f"[bold red]✖ Error:[/bold red] Failed to reset project: {e}")
