import yaml
import click
from pathlib import Path
from doclify.utils.scanner import scan_repo

def init_project():
    """
    Initialize or reinitialize a Doclify project.
    """
    config_path = Path("doclify.yaml")
    is_reinit = config_path.exists()

    try:
        repo_structure = scan_repo()
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(repo_structure, f, default_flow_style=False)

    except Exception as e:
        click.echo(f"Error: Failed to initialize project: {e}", err=True)
        return

    action = "Reinitialized" if is_reinit else "Initialized"
    click.echo(f"{action} doclify in the repository {Path.cwd().name}")