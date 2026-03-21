import time
import re
import os
from pathlib import Path
from rich.console import Console
from typing import Optional
from doclify.utils.llm import generate_doc
from doclify.utils.logger import get_logger
from doclify.schema.schema import LLMConfig, ReadmeResponse

# Initialize logger and console
logger = get_logger(__name__)
console = Console()

def generate_readme_file(cache, config, llm_config: Optional[LLMConfig] = None, metadata: Optional[dict] = None):
    """
    Generates the final README with clean uv-style output.
    """
    files = config.get("structure", [])
    if not files:
        logger.warning("README generation aborted: No files in structure.")
        console.print("[bold yellow]⚠ Warning:[/bold yellow] No files found in configuration structure.")
        return False

    logger.info("Starting README aggregation and generation.")
    
    with console.status("[bold cyan]Generating[/bold cyan] README.md", spinner="dots"):
        file_summaries = []
        norm_files = {os.path.normpath(f) for f in files}
        for file_path, summary in cache.get("files", {}).items():
            if os.path.normpath(file_path) in norm_files: 
                 file_summaries.append(f"## File: {file_path}\n\n{summary}")
        
        if file_summaries:
            aggregated_summaries = "\n\n".join(file_summaries)
            # Use ReadmeResponse static schema for structured output
            response = generate_doc(
                aggregated_summaries, 
                prompt_type="final_summary", 
                llm_config=llm_config,
                metadata=metadata
            )
            
            # Since generate_doc now returns pure string representations:
            final_readme = response.strip() if response else ""

            # --- ROBUST MARKDOWN CLEANING ---
            # Sometimes LLMs wrap the markdown content again in ```markdown ... ``` 
            # within the JSON field. Let's strip that.
            final_readme = final_readme.strip()
            if final_readme.startswith("```"):
                # Use re to strip the wrapper but keep the content
                inner_match = re.search(r'```(?:markdown|md)?\s*(.*?)\s*```', final_readme, re.DOTALL)
                if inner_match:
                    final_readme = inner_match.group(1).strip()
                else:
                    # Fallback strip
                    final_readme = re.sub(r'^```[a-z]*\n?', '', final_readme)
                    final_readme = re.sub(r'\n?```$', '', final_readme).strip()
        else:
            logger.warning("No summaries found in cache for README.")
            final_readme = "# Project Documentation\n\nNo summaries available."

        # Creating a directory for created READMEs
        version_dir = Path(".doclify/generated_artifacts/")
        version_dir.mkdir(parents=True, exist_ok=True) # Ensure parents created
        artifact_path = version_dir / f"README-{time.strftime('%Y%m%d%H%M%S')}.md"
        artifact_path.write_text(final_readme, encoding="utf-8")
        logger.info(f"Versioned artifact saved to {artifact_path}")

        readme_path = Path("README.md")
        if readme_path.exists():
            backup_path = Path(f"README-prev-{time.strftime('%Y%m%d%H%M%S')}.md")
            try:
                readme_path.rename(backup_path)
                logger.info(f"Existing README backed up to {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to backup README: {e}")

        readme_path.write_text(final_readme, encoding="utf-8")
        logger.info("README.md successfully updated.")

    return True
