import yaml
import os
from pathlib import Path
from rich.console import Console
from doclify.utils.scanner import scan_repo
from doclify.utils.logger import get_logger
from doclify.config.constants import LiteLLMConfig

logger = get_logger(__name__)
console = Console()

def init_project():
    """
    Initializing or Re-Initializing the Doclify Project    
    """
    
    # 1. Defining Yaml Path Configuration and Checking the existence of it
    # ----------------------------------------------------------------------------------------------------

    logger.info(f"Init sequence started. Directory: {Path.cwd()}")
    config_path = Path("doclify.yaml")
    is_reinit = config_path.exists()


    # 2. Scanning the Repository Structure
    # ----------------------------------------------------------------------------------------------------

    try:        
        with console.status("[bold cyan]Analyzing[/bold cyan] Repository Structure", spinner="arc"):
            repo_structure = scan_repo()
            logger.info(f"Scan complete. Found {len(repo_structure.get('structure', []))} File Nodes.")


        # 3. Handling .gitignore
        # ----------------------------------------------------------------------------------------------------
            
        gitignore_path = Path(".gitignore")
        doclify_ignore = ".doclify/"
        
        try:
            if gitignore_path.exists():
                # If .gitignore exists
                content = gitignore_path.read_text(encoding="utf-8")
                if doclify_ignore not in content.splitlines():
                    logger.info("Adding .doclify/ to .gitignore file")
                    suffix = "\n" if not content.endswith("\n") else ""
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write(f"{suffix}{doclify_ignore}\n")
            else:
                # If .gitignore does not exist, create it
                logger.info("Creating new .gitignore file")
                gitignore_path.write_text(f"{doclify_ignore}\n", encoding="utf-8")

        except Exception as git_err:
            logger.warning(f"Could not update .gitignore: {git_err}")

        # 4. Customizing the Yaml File
        # ----------------------------------------------------------------------------------------------------

        final_config = {
            "project": repo_structure.get("project", Path.cwd().name),
            "structure": repo_structure.get("structure", []),
            "llm": {
                "model": LiteLLMConfig.DEFAULT_MODEL
            }
        }

        # 5. Writing the Yaml Configuration
        # ----------------------------------------------------------------------------------------------------

        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(final_config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Configuration written to {config_path}")
        
        except Exception as write_err:
            logger.error(f"Failed to write configuration: {write_err}")
            raise

    except Exception as e:
        logger.error(f"Doclify Initialization Failed: {str(e)}", exc_info=True)
        console.print(f"\n[bold red]✖ Error:[/bold red] Failed to Initialize Doclify. {str(e)}")
        return

    # 6. Displaying Success Message
    # ----------------------------------------------------------------------------------------------------

    action = "Reinitialized" if is_reinit else "Initialized"
    console.print(f"[bold green]✔ {action}[/bold green] [blue]{config_path}[/blue]")
    console.print(f"\n[bold cyan]Next steps[/bold cyan]")
    console.print(f"  • Review [blue]{config_path}[/blue] to customize included files")
    console.print(f"  • Run [bold green]doclify run[/bold green] to generate documentation")
    
    logger.info(f"Init process completed successfully.")
