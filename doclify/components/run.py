import yaml
import click
import time
import os
import json
import re
from pathlib import Path
from rich.console import Console
from doclify.utils.extract import extract_file_content
from doclify.utils.llm import generate_doc
from doclify.utils.file_utils import load_cache, save_cache
from doclify.config.constants import LiteLLMConfig
from doclify.schema.schema import FileSummaries, LLMConfig
from doclify.utils.readme import generate_readme_file
from doclify.utils.logger import get_logger

# Initialize production-level logger and clean console
logger = get_logger(__name__)
console = Console()

def run_docs(model=None, provider=None):
    """
    Generates documentation with a clean 'uv' inspired UI.
    Detailed logic is captured in .doclify/logs/
    """
    logger.info(f"Starting documentation generation pipeline. Overrides: model={model}, provider={provider}")
    start_time = time.time()

    # API Key validation is now handled lazily by LiteLLM.
    # Users will get a clear error if their specific provider key is missing.

    # 2. Config Validation
    config_path = Path("doclify.yaml")
    if not config_path.exists():
        logger.warning(f"Configuration file {config_path} missing.")
        console.print("[bold red]✖ Error:[/bold red] [blue]doclify.yaml[/blue] not found. Run [bold green]doclify init[/bold green] first.")
        return

    try:
        # Load Config
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        files = config.get("structure", [])
        
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
        
        if not files:
            logger.warning("No files found in doclify.yaml structure.")
            console.print("[bold yellow]⚠ Warning:[/bold yellow] No files found in [blue]doclify.yaml[/blue]")
            return

        # UV-style initial summary
        console.print(f"[bold cyan]Found[/bold cyan] [white]{len(files)} Files[/white] to Process")
        
        cache = load_cache()
        all_file_contents = []
        
        # 3. Reading Phase (Spinner disappears after)
        with console.status("[bold cyan]Reading[/bold cyan] project files...", spinner="dots"):
            for file_path in files:
                logger.debug(f"Extracting: {file_path}")
                content = extract_file_content(file_path)
                if not (content.startswith("Error") or content.startswith("File not found")):
                    all_file_contents.append((file_path, f"--- FILE: {file_path} ---\n{content}\n"))
                else:
                    logger.warning(f"Skipping {file_path}: {content[:50]}...")
            
            if not all_file_contents:
                logger.error("No valid file content found to process.")
                console.print("[bold yellow]⚠ Warning:[/bold yellow] No valid file content found to process.")
                return

        logger.info(f"Extracted content from {len(all_file_contents)} files. Starting summarization.")

        # 4. Summarization Phase (Count updates, spinner disappears after)
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
                new_summaries = summaries_model.root
                # Filter: Only keep keys that were actually in the batch
                return {k: v for k, v in new_summaries.items() if k in batch_files}
            except Exception as e:
                logger.error(f"Error in batch {batch_files}: {str(e)}", exc_info=True)
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
                    
                    processed_count += len(futures[future])
                    status.update(f"[bold cyan]Processing[/bold cyan] Files ({processed_count}/{total_files})...")

        # 5. Final README Generation
        generate_readme_file(cache, config, llm_config=llm_config)
        
        # Final success message with duration
        duration = time.time() - start_time
        console.print(f"[bold green]Generated[/bold green] README.md in [white]{duration:.1f} secs[/white]")
        logger.info(f"Pipeline completed successfully in {duration:.2f}s")

    except Exception as e:
        logger.critical(f"Pipeline failed: {str(e)}", exc_info=True)
        console.print(f"[bold red]✖ Failed[/bold red] to generate Documentation: {e}")