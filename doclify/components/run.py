import yaml
import time
import os
from typing import Optional
from pathlib import Path
from rich.console import Console
from doclify.utils.extract import extract_file_content
from doclify.utils.llm import generate_doc
from doclify.utils.file_utils import load_cache, save_cache, clean_cache
from doclify.config.constants import LiteLLMConfig
from doclify.schema.schema import LLMConfig
from doclify.utils.readme import generate_readme_file
from doclify.utils.logger import get_logger

# Initialize production-level logger and clean console
logger = get_logger(__name__)
console = Console()

def run_docs(model=None, provider=None):
    """
    Generates documentation with a 200k token-based batching strategy.
    """
    logger.info(f"Starting documentation generation pipeline. Overrides: model={model}")
    start_time = time.time()

    # 1. Yaml Config Validation
    # ----------------------------------------------------------------------------------------------------

    config_path = Path("doclify.yaml")
    if not config_path.exists():
        logger.warning(f"Configuration file {config_path} missing.")
        console.print("[bold red]✖ Error:[/bold red] [blue]doclify.yaml[/blue] not found. Run [bold green]doclify init[/bold green] first.")
        return

    # 2. Retreiving Files and Language Model from the Yaml Config File
    # ----------------------------------------------------------------------------------------------------

    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        logger.info(f"doclify.yaml found and loaded successfully.")

        # 2.1 Retreiving Files and Language Model
        # ----------------------------------------------------------------------------------------------------
        files = config.get("structure", [])
        llm_model = config.get("llm", {}).get("model", "")
        generate_readme = True # Default to True
        logger.info(f"Retrieved {len(files)} files from doclify.yaml.")
        logger.info(f"Retrieved {llm_model} model from doclify.yaml.")

        # 2.2 Data Handling and Validation
        # ----------------------------------------------------------------------------------------------------
        if not llm_model or not llm_model.strip():
            llm_model = LiteLLMConfig.DEFAULT_MODEL
        
        # Load configuration
        # The `config` variable is already loaded above.
        llm_config_data = config.get("llm", {})
        llm_config = LLMConfig(**llm_config_data)

        # Apply CLI overrides
        if model:
            llm_config.model = model
        if provider:
            llm_config.provider = provider

        session_id = time.strftime("%Y-%m-%d_%H-%M:%S")
        project_name = config.get("project_name", os.path.basename(os.getcwd()))
        llm_metadata = {"session_id": session_id, "project_name": project_name}

        if not files:
            logger.warning("No files found in doclify.yaml structure.")
            console.print("[bold yellow]⚠ Warning:[/bold yellow] No files found in [blue]doclify.yaml[/blue]")
            return

        # 2.3 Cache Handling
        # ----------------------------------------------------------------------------------------------------
        logger.info("Initializing cache for file summaries.")
        cache = load_cache()

        # If cache doesn't exist, initialize it
        if "files" not in cache:
            cache["files"] = {}
        
        # If any files are missing in cache, initialize them
        for f in files:
            if f not in cache["files"]:
                cache["files"][f] = ""
        
        # --- CACHE CLEANING ---
        # Remove any keys from cache["files"] that are NOT in the doclify.yaml structure
        cache = clean_cache(cache, files)
        save_cache(cache)

        console.print(f"[bold cyan]Found[/bold cyan] [white]{len(files)} Files[/white] to Process")
        
        extracted_files = []
        
        # 3. File Reading Phase
        # ----------------------------------------------------------------------------------------------------
        with console.status("[bold cyan]Extracting[/bold cyan] Repository Files", spinner="dots"):
            for file_path in files:
                chunks = extract_file_content(file_path)
                if not any(c.startswith("Error") or c.startswith("File not found") for c in chunks):
                    tokens = sum(len(c) for c in chunks) // 4 # Basic token estimation
                    extracted_files.append({"path": file_path, "chunks": chunks, "tokens": tokens})
                else:
                    logger.warning(f"Skipping {file_path} due to extraction errors.")
            
        if not extracted_files:
            logger.error("No valid file content found to process.")
            console.print("[bold yellow]⚠ Warning:[/bold yellow] No valid file content found to process.")
            return


        # 4. Processing Each Extracted File and Generating Summaries
        # ----------------------------------------------------------------------------------------------------

        def process_file(item, llm_config: Optional[LLMConfig] = None, metadata: Optional[dict] = None):
            """
            Processes a single file and generates a documentation summary for it.
            """
            file_path = item["path"]
            chunks = item["chunks"]
            summaries = []
            
            for chunk in chunks:
                try:
                    summary = generate_doc(
                        code_content=chunk, 
                        prompt_type="batch_summary", 
                        llm_config=llm_config,
                        metadata=metadata
                    )
                    if summary:
                        summaries.append(summary.strip())
                except Exception as e:
                    logger.error(f"Error processing chunk for {file_path}: {str(e)}", exc_info=True)
            
            return item, "\n\n".join(summaries) if summaries else ""

        total_files = len(extracted_files)
        processed_count = 0

        for item in extracted_files:
            with console.status(f"[bold cyan]Summarizing[/bold cyan] ({processed_count}/{total_files})...", spinner="dots"):
                item_ret, summary = process_file(item, llm_config=llm_config, metadata=llm_metadata)
            
            if summary:
                norm_path = os.path.normpath(item["path"])
                cache["files"][norm_path] = summary
                
            processed_count += 1
        
        save_cache(cache)

        # Final README generation
        if generate_readme:
            generate_readme_file(cache, config, llm_config=llm_config, metadata=llm_metadata)
        
        duration = time.time() - start_time
        console.print(f"[bold green]Generated[/bold green] README.md in [white]{duration:.1f} secs[/white]")
        logger.info(f"Pipeline completed successfully in {duration:.2f}s")

    except Exception as e:
        logger.critical(f"Pipeline failed: {str(e)}", exc_info=True)
        console.print(f"[bold red]✖ Failed[/bold red] to generate Documentation: {e}")
