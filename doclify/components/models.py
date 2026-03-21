import os
from groq import Groq
from rich.console import Console
from rich.table import Table

console = Console()

def list_models():
    """Fetches and displays all available models from Groq in a rich table."""
    try:
        api_key = os.environ.get("GROQ_API_KEY", "").strip()
        if not api_key:
            console.print("\n[bold red]✖ Error:[/bold red] Missing GROQ_API_KEY. Please configure your environment variables first.")
            return
            
        client = Groq(api_key=api_key)
        
        with console.status("[bold cyan]Fetching available models from Groq...[/bold cyan]", spinner="dots"):
            models_response = client.models.list()
            
        # Sort models alphabetically by Developer, then by Model ID
        models_sorted = sorted(
            models_response.data, 
            key=lambda x: (str(getattr(x, 'owned_by', 'Unknown') or 'Unknown').lower(), str(getattr(x, 'id', '')).lower())
        )
        
        # Build a beautiful Rich table
        table = Table(
            title_style="bold magenta", 
            border_style="blue", 
            show_header=True, 
            header_style="bold cyan"
        )
        table.add_column("Model ID", justify="left", style="white")
        table.add_column("Developer", justify="left", style="green")
        table.add_column("Context", justify="right", style="yellow")
        table.add_column("Max Output", justify="right", style="cyan")
        
        for md in models_sorted:
            # Format token numbers into 'k' format for easier reading
            ctx = getattr(md, 'context_window', None)
            ctx_str = f"{ctx // 1024}k" if ctx and ctx >= 1024 else str(ctx or "N/A")
            
            out = getattr(md, 'max_completion_tokens', None)
            out_str = f"{out // 1024}k" if out and out >= 1024 else str(out or "N/A")
            
            table.add_row(
                f"• {getattr(md, 'id', 'Unknown')}",
                getattr(md, 'owned_by', 'Unknown'),
                ctx_str,
                out_str
            )
            
        console.print()
        console.print(table)
            
    except Exception as e:
        console.print(f"\n[bold red]✖ Failed to fetch models:[/bold red] {str(e)}")
