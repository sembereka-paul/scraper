import click
from main import get_categories, read_a_product, get_category_products
import json

@click.group()
def cli():
    """Top-level CLI."""
    pass

@cli.command('list')
def list_categories():
    """List categories."""
    click.echo(json.dumps(get_categories()))

@cli.group()
def categories():
    """Manage categories."""
    pass

@categories.command('products')
@click.argument('category_id', required=False, default='128-dyr')
def list_category_products(category_id):
    """List products for a category."""
    click.echo(json.dumps(get_category_products(category_id)))

@cli.group()
def products():
    """List products"""
    pass

@products.command('read')
@click.argument('path')
def list_products(path):
    """List products for a category."""
    click.echo(json.dumps(read_a_product(path)))

if __name__ == '__main__':
    cli()
