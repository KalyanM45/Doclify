import json
from pathlib import Path
from doclify.utils.logger import get_logger

# Initialize the logger
logger = get_logger(__name__)

MAX_FILE_SIZE = 1_000_000 # 1MB
CHUNK_SIZE_LIMIT = 40_000 # Roughly 10k tokens

def extract_file_content(file_path: str) -> list[str]:
    """
    Reads and returns the content of the file partitioned into chunks for LLM consumption.
    """
    path = Path(file_path)
    if not path.exists():
        logger.warning(f"File not found: {file_path}")
        return [f"File not found: {file_path}"]
    
    # Size check
    try:
        if path.stat().st_size > MAX_FILE_SIZE:
            logger.warning(f"Skipping large file: {file_path} ({path.stat().st_size} bytes)")
            return [f"File too large to process: {file_path}"]
    except Exception as e:
        logger.error(f"Error checking size of {file_path}: {e}")
        return [f"Error checking file size: {file_path}"]

    try:
        ext = path.suffix.lstrip(".") or "txt"
        
        if path.suffix == ".ipynb":
            with open(path, "r", encoding="utf-8") as f:
                nb_content = json.load(f)
            
            code_lines = []
            for cell in nb_content.get("cells", []):
                if cell.get("cell_type") == "code":
                    source = cell.get("source", [])
                    if isinstance(source, list):
                        code_lines.extend(source)
                        code_lines.append("\n\n")
                    else:
                        code_lines.append(source)
                        code_lines.append("\n\n")
            
            content = "".join(code_lines).strip()
            display_ext = "python"
        else:
            content = path.read_text(encoding="utf-8")
            display_ext = ext
        
        logger.info(f"Extraction successful for {file_path}")
        
        # Chunk logic
        if len(content) > CHUNK_SIZE_LIMIT:
            chunks = [content[i:i+CHUNK_SIZE_LIMIT] for i in range(0, len(content), CHUNK_SIZE_LIMIT)]
            return [f"File: {file_path} (Part {i+1}/{len(chunks)})\n```{display_ext}\n{chunk}\n```" for i, chunk in enumerate(chunks)]
        
        return [f"File: {file_path}\n```{display_ext}\n{content}\n```"]
        
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
        return [f"Error reading file {file_path}: {e}"]