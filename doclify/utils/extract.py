from pathlib import Path

def extract_file_content(file_path: str) -> str:
    """
    Reads and returns the content of the file.
    Example output format:
    File: <path>
    ```<extension>
    <content>
    ```
    """
    path = Path(file_path)
    if not path.exists():
        return f"File not found: {file_path}"
    
    try:
        content = path.read_text(encoding="utf-8")
        ext = path.suffix.lstrip(".") or "txt"
        return f"File: {file_path}\n```{ext}\n{content}\n```"
    except Exception as e:
        return f"Error reading file {file_path}: {e}"
