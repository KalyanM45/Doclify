import pathspec
from pathlib import Path

def scan_repo():
    patterns = []

    # Built-in Python gitignore
    try:
        from importlib.resources import files
        builtin_ignore = files("doclify.resources").joinpath("Python.gitignore")
        if builtin_ignore.is_file():
            patterns.extend(builtin_ignore.read_text(encoding="utf-8").splitlines())
    except Exception as e:
        # Fallback or log error if needed
        pass

    # User project .gitignore
    project_gitignore = Path(".gitignore")
    if project_gitignore.exists():
        patterns.extend(project_gitignore.read_text().splitlines())

    spec = pathspec.PathSpec.from_lines("gitwildmatch", patterns)

    files = [
        str(p)
        for p in Path(".").rglob("*")
        if p.is_file()
        and not spec.match_file(p)
        and p.stat().st_size > 0
        and p.suffix in {".py", ".md", ".txt"}
    ]

    return {
        "project": Path.cwd().name,
        "structure": files
    }