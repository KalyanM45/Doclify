import yaml
import tempfile
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
    Initialize or reinitialize a Doclify project with fixed YAML order and atomic safety.
    """
    config_path = Path("doclify.yaml")
    is_reinit = config_path.exists()
    
    logger.info(f"Init sequence started. Directory: {Path.cwd()}")

    try:        
        with console.status("[bold cyan]Analyzing[/bold cyan] repository structure...", spinner="dots"):
            repo_structure = scan_repo()
            logger.info(f"Scan complete. Found {len(repo_structure.get('structure', []))} file nodes.")
            
        # Handle .gitignore
        gitignore_path = Path(".gitignore")
        doclify_ignore = ".doclify/"
        
        try:
            if gitignore_path.exists():
                content = gitignore_path.read_text(encoding="utf-8")
                if doclify_ignore not in content.splitlines():
                    logger.info("Appending .doclify/ to .gitignore")
                    suffix = "\n" if not content.endswith("\n") else ""
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write(f"{suffix}{doclify_ignore}\n")
            else:
                logger.info("Creating new .gitignore")
                gitignore_path.write_text(f"{doclify_ignore}\n", encoding="utf-8")
        except Exception as git_err:
            logger.warning(f"Could not update .gitignore: {git_err}")

        # Construct dictionary in specific order (project -> structure -> llm)
        final_config = {
            "project": repo_structure.get("project", Path.cwd().name),
            "structure": repo_structure.get("structure", []),
            "llm": {
                "model": LiteLLMConfig.DEFAULT_MODEL
            }
        }

        # Atomic Write (Removed "Writing" spinner as requested)
        fd, temp_path = tempfile.mkstemp(dir=".", prefix="doclify_cfg_", suffix=".tmp")
        try:
            with os.fdopen(fd, 'w', encoding="utf-8") as f:
                # sort_keys=False preserves the order defined in the final_config dict
                yaml.dump(final_config, f, default_flow_style=False, sort_keys=False)
            
            os.replace(temp_path, config_path)
            logger.info(f"Configuration atomically written to {config_path}")
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}", exc_info=True)
        console.print(f"\n[bold red]✖ Error:[/bold red] Failed to initialize project.")
        return

    action = "Reinitialized" if is_reinit else "Initialized"
    console.print(f"[bold green]✔ {action}[/bold green] [blue]{config_path}[/blue]")
    console.print(f"\n[bold cyan]Next steps[/bold cyan]")
    console.print(f"  • Review [blue]{config_path}[/blue] to customize included files")
    console.print(f"  • Run [bold green]doclify run[/bold green] to generate documentation")
    
    logger.info(f"Init process completed successfully.")
