import click
from doclify.components.init import init_project
from doclify.components.refresh import refresh_project

from doclify import __version__

@click.group()
@click.version_option(version=__version__)
def cli():
    pass

@cli.command()
def init():
    init_project()

@cli.command()
def refresh():
    refresh_project()

@cli.command()
@click.option('--model', help='Override the LLM model.')
@click.option('--provider', help='Override the LLM provider.')
def run(model, provider):
    from doclify.components.run import run_docs
    run_docs(model=model, provider=provider)

@cli.command()
def reset():
    from doclify.components.reset import reset_project
    reset_project()

@cli.command()
@click.argument('path', type=click.Path(exists=True), required=True)
@click.option('--model', help='Override the LLM model.')
@click.option('--provider', help='Override the LLM provider.')
def update(path, model, provider):
    from doclify.components.update import update_docs
    update_docs(path, model=model, provider=provider)