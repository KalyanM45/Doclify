import click
from docly.components.init import init_project

@click.group()
def cli():
    pass

@cli.command()
def init():
    init_project()