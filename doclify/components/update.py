import click
import time
import yaml
import json
import re
import os
from pathlib import Path
from rich.console import Console
from rich.prompt import Confirm  # <--- Added this import
from doclify.utils.file_utils import load_cache, save_cache
from doclify.utils.extract import extract_file_content
from doclify.utils.llm import generate_doc
from doclify.config.constants import LiteLLMConfig
from doclify.schema.schema import FileSummaries, LLMConfig
from doclify.utils.readme import generate_readme_file
from doclify.utils.logger import get_logger

# Initialize production-level logger and clean console
logger = get_logger(__name__)
console = Console()

def update_docs(path, model=None, provider=None):
    """
    Update documentation for a specific file or all files (use '.').
    Logs all steps to .doclify/logs/ with a clean uv-style UI.
    """
    start_time = time.time()
    logger.info(f"Update sequence triggered for path: {path}. Overrides: model={model}, provider={provider}")
    config_path = Path("doclify.yaml")
    files_to_process = []

    if path == ".":
        logger.info("Universal update ('.') requested.")
        if not config_path.exists():
            logger.error("doclify.yaml missing during universal update.")
            console.print("[bold red]✖ Error:[/bold red] [blue]doclify.yaml[/blue] not found. Run [bold green]doclify init[/bold green] first.")
            return
        
        try:
            config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
            files_to_process = config.get("structure", [])
            
            # Load LLM Config
            llm_data = config.get("llm", {})
            llm_config = LLMConfig(**llm_data) if llm_data else None
            
            # CLI Overrides
            if llm_config:
                if model: llm_config.model = model
                if provider: llm_config.provider = provider
            elif model or provider:
                llm_config = LLMConfig(
                    model=model or LiteLLMConfig.DEFAULT_MODEL,
                    provider=provider
                )
            
            logger.info(f"Loaded {len(files_to_process)} files from configuration for update.")
        except Exception as e:
            logger.error(f"Failed to read doclify.yaml: {str(e)}", exc_info=True)
            console.print(f"[bold red]✖ Error:[/bold red] Error reading [blue]doclify.yaml[/blue]: {e}")
            return
    else:
        logger.info(f"Single file update requested for: {path}")
        files_to_process = [path]

    if not files_to_process:
        logger.warning("Update list is empty. Nothing to process.")
        console.print("[bold yellow]⚠ Warning:[/bold yellow] No files found to update.")
        return

    try:
        cache = load_cache()
    except Exception as e:
        logger.warning(f"Failed to load cache: {e}")
        cache = {"files": {}}

    all_file_contents = []
    
    # 1. Reading Phase (Indicator disappears after completion)
    with console.status(f"[bold cyan]Reading[/bold cyan] project files...", spinner="dots"):
        for file_path in files_to_process:
            logger.debug(f"Extracting content for update: {file_path}")
            content = extract_file_content(file_path)
            if not (content.startswith("Error") or content.startswith("File not found")):
                all_file_contents.append((file_path, f"--- FILE: {file_path} ---\n{content}\n"))
            else:
                logger.warning(f"File content extraction failed for {file_path}: {content[:50]}...")
    
    if not all_file_contents:
        logger.error("No valid file content found to update.")
        console.print("[bold yellow]⚠ Warning:[/bold yellow] No valid file content found to process.")
        return

    # 2. Summarization Phase (Count updates live, indicator disappears after)
    batch_size = 5
    total_files = len(all_file_contents)
    
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_batch(batch):
        batch_files = [item[0] for item in batch]
        batch_content = "\n".join([item[1] for item in batch])
        try:
            summaries_model = generate_doc(
                batch_content, 
                type="batch_summary", 
                json_format=FileSummaries,
                llm_config=llm_config
            )
            return summaries_model.root
        except Exception as e:
            logger.error(f"Error during update batch {batch_files}: {str(e)}", exc_info=True)
            return {}

    with console.status(f"[bold cyan]Processing[/bold cyan] Files (0/{total_files})...", spinner="dots") as status:
        batches = [all_file_contents[i:i + batch_size] for i in range(0, total_files, batch_size)]
        processed_count = 0

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {executor.submit(process_batch, b): b for b in batches}
            
            for future in as_completed(futures):
                batch_results = future.result()
                if batch_results:
                    if "files" not in cache:
                        cache["files"] = {}
                    cache["files"].update(batch_results)
                    save_cache(cache)
                    logger.info(f"Cache chunk updated successfully.")
                
                processed_count += len(futures[future])
                status.update(f"[bold cyan]Processing[/bold cyan] Files ({processed_count}/{total_files})...")
    
    # Success message matching the 'uv' aesthetic
    if path == ".":
        console.print(f"[bold green]Updated[/bold green] artifacts for [white]all files[/white]")
    else:
        console.print(f"[bold green]Updated[/bold green] artifacts for [white]{path}[/white]")

    # 3. Final README Decision (Using Rich Confirm)
    logger.info("Prompting user for README regeneration.")
    if Confirm.ask("Regenerate README with latest changes?"):
        logger.info("User confirmed README regeneration.")
        # Load config again to ensure we have the latest structure for generate_readme_file
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        duration = time.time() - start_time
        generate_readme_file(cache, config, llm_config=llm_config)
        console.print(f"[bold green]Generated[/bold green] README.md in [white]{duration:.1f} secs[/white]")
    else:
        logger.info("User declined README regeneration.")