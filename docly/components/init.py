import yaml
import click
from pathlib import Path
from docly.utils.scanner import scan_repo
from docly.utils.logger import get_logger

logger = get_logger(__name__)

def init_project():
    """
    Initialize or reinitialize the docly.yaml configuration file.
    """
    path = Path("docly.yaml")
    logger.info(f"Initializing docly configuration in {path}")
    try:
        data = scan_repo()
        path.write_text(
            yaml.dump(data, sort_keys=False),
            encoding="utf-8"
        )
        logger.info(f"Initialized docly configuration in {path}")

        if path.exists():
            click.echo(f"Reinitialized existing docly configuration in {path}")
        else:
            click.echo(f"Initialized docly configuration in {path}")

    except Exception as e:
        raise click.ClickException(
            f"Failed to initialize docly configuration: {e}"
        )
