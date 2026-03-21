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
        with console.status("[bold cyan]Analyzing[/bold cyan] Repository Structure", spinner="dots"):
            repo_structure = scan_repo()
        
        logger.info(f"Scan complete. Found {len(repo_structure.get('structure', []))} File Nodes.")


        # 3. Handling .gitignore
        # ----------------------------------------------------------------------------------------------------
            
        gitignore_path = Path(".gitignore")
        doclify_ignores = [".doclify/", "doclify.yaml"]
        
        try:
            lines = []
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                # Keep original lines and avoid duplicates
                lines = [line.strip() for line in content.splitlines() if line.strip()]
            
            # Add missing ignores
            added_any = False
            for entry in doclify_ignores:
                if entry not in lines:
                    lines.append(entry)
                    added_any = True
                    logger.info(f"Adding {entry} to .gitignore")

            if added_any or not gitignore_path.exists():
                # Write back with proper newlines
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(lines) + "\n")
                logger.info(".gitignore updated successfully")

        except Exception as git_err:
            logger.warning(f"Could not update .gitignore: {git_err}")

        # 4. Customizing the Yaml File
        # ----------------------------------------------------------------------------------------------------

        # Load existing config if it exists to preserve extra fields
        existing_config = {}
        if is_reinit:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    existing_config = yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Could not read existing config: {e}")

        # Merge strategy: preserve existing values, provide placeholders for others
        llm_defaults = {
            "model": LiteLLMConfig.DEFAULT_MODEL
        }
        
        # Merge existing into defaults to preserve what's there and add what's missing
        llm_config = {**llm_defaults, **existing_config.get("llm", {})}
        
        final_config = {
            "project": existing_config.get("project") or repo_structure.get("project", Path.cwd().name),
            "structure": repo_structure.get("structure", []),
            "llm": llm_config
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
