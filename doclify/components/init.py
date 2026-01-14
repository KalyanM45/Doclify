import yaml
import click
from pathlib import Path
from doclify.utils.scanner import scan_repo
from doclify.utils.logger import get_logger

logger = get_logger(__name__)

def init_project():
    """
    Initializes a new Doclify project.
    Scans the repository and creates a doclify.yaml file.
    """
    config_path = Path("doclify.yaml")
    if config_path.exists():
        click.echo(f"doclify.yaml already exists. Skipping initialization.")
        return

    click.echo("Scanning repository...")
    
    try:
        # Analyze the repo structure
        repo_structure = scan_repo()
        
        # Save to doclify.yaml
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(repo_structure, f, default_flow_style=False)

        click.echo(f"Success! Initialized doclify.yaml with {len(repo_structure['structure'])} files found.")
    except Exception as e:
        click.echo(f"Error: Failed to initialize project: {e}", err=True)
