import yaml
from pathlib import Path
from rich.console import Console
from doclify.utils.logger import get_logger

logger = get_logger(__name__)
console = Console()

def update_config(model=None):
    """
    Updates the doclify.yaml configuration with new LLM settings while preserving order.
    """

    # 1. Defining Configuration of Yaml File
    # ----------------------------------------------------------------------------------------------------
    
    config_path = Path("doclify.yaml")
    if not config_path.exists():
        console.print("[bold red]✖ Error:[/bold red] [blue]doclify.yaml[/blue] not found. Run [bold green]doclify init[/bold green] first.")
        return

    # 2. Loading and Updating the Yaml File with Given Model
    # ----------------------------------------------------------------------------------------------------

    try:
        content = yaml.safe_load(config_path.read_text(encoding="utf-8"))

        # 2.1 Checking the existence of LLM in the Yaml File
        # ----------------------------------------------------------------------------------------------------
        
        if "llm" not in content:
            content["llm"] = {}

        if model:
            content["llm"]["model"] = model

        # 3. Writing the Yaml Configuration
        # ----------------------------------------------------------------------------------------------------
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(content, f, default_flow_style=False, sort_keys=False)
            
        logger.info(f"Config updated: {content}")
        
        # 4. Displaying Success Message
        # ----------------------------------------------------------------------------------------------------
        
        console.print(f"[bold green]✔ Updated[/bold green] [blue]Default Model[/blue] configuration: [cyan]{model}[/cyan]")

    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        console.print(f"[bold red]✖ Error:[/bold red] Could not update configuration. {e}")
