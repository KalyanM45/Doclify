import pathspec
from pathlib import Path

def scan_repo(include: list = None, exclude: list = None):
    patterns = []
    
    # Custom Excludes from config
    if exclude:
        patterns.extend(exclude)

    # Built-in Python gitignore
    try:
        from importlib.resources import files
        builtin_ignore = files("doclify.resources").joinpath("Python.gitignore")
        if builtin_ignore.is_file():
            patterns.extend(builtin_ignore.read_text(encoding="utf-8").splitlines())
    except Exception:
        pass

    # User project .gitignore
    project_gitignore = Path(".gitignore")
    if project_gitignore.exists():
        patterns.extend(project_gitignore.read_text().splitlines())

    spec = pathspec.PathSpec.from_lines("gitignore", patterns)
    
    # Custom includes
    include_patterns = set(include) if include else None

    files = []
    for p in Path(".").rglob("*"):
        if p.is_file() and not spec.match_file(p) and p.stat().st_size > 0:
            str_path = str(p)
            # Apply suffix filter
            if p.suffix in {".py", ".md", ".txt", ".ipynb"}:
                # Apply include filter if defined
                if not include_patterns or any(str_path == inc or str_path.startswith(inc) for inc in include_patterns):
                    files.append(str_path)

    return {
        "project": Path.cwd().name,
        "structure": files
    }