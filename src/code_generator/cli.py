"""
CLI interface for CRUD generator.
"""
import click
import importlib
import inspect
from pathlib import Path
from typing import Optional

from .generator import CRUDGenerator


@click.command()
@click.argument('model_path', help='Path to model (e.g., josi.models.person_model.Person)')
@click.option('--module', '-m', help='Module name (e.g., person)', required=True)
@click.option('--skip-existing/--overwrite', default=True, help='Skip existing files')
@click.option('--no-graphql', is_flag=True, help='Skip GraphQL schema generation')
@click.option('--base-path', default='src/josi', help='Base path for generated files')
def generate_crud(
    model_path: str,
    module: str,
    skip_existing: bool,
    no_graphql: bool,
    base_path: str
):
    """
    Generate CRUD operations for a SQLModel.
    
    Example:
        python -m code_generator.cli josi.models.person_model.Person --module person
    """
    try:
        # Import the model
        module_path, class_name = model_path.rsplit('.', 1)
        module_obj = importlib.import_module(module_path)
        model_class = getattr(module_obj, class_name)
        
        # Verify it's a SQLModel
        if not hasattr(model_class, '__tablename__'):
            click.echo(f"Error: {class_name} doesn't appear to be a SQLModel", err=True)
            return
        
        # Create generator
        generator = CRUDGenerator(base_path)
        
        # Generate files
        click.echo(f"Generating CRUD for {class_name}...")
        generated = generator.generate_crud(
            model_class=model_class,
            module_name=module,
            skip_existing=skip_existing,
            include_graphql=not no_graphql
        )
        
        # Report results
        if generated:
            click.echo("Generated files:")
            for file_type, file_path in generated.items():
                click.echo(f"  ✓ {file_type}: {file_path}")
        else:
            click.echo("No files generated (all already exist)")
        
        click.echo("\nNext steps:")
        click.echo(f"1. Add the router to your API:")
        click.echo(f"   from josi.api.v1.controllers.{module}_controller import router as {module}_router")
        click.echo(f"   app.include_router({module}_router)")
        click.echo(f"\n2. Update GraphQL schema if generated:")
        click.echo(f"   Add {class_name}Query and {class_name}Mutation to your schema")
        
    except ImportError as e:
        click.echo(f"Error: Could not import {model_path}: {e}", err=True)
    except AttributeError as e:
        click.echo(f"Error: {class_name} not found in {module_path}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


def create_crud_for_model(
    model_class,
    module_name: str,
    skip_existing: bool = True,
    include_graphql: bool = True,
    base_path: str = "src/josi"
) -> dict:
    """
    Programmatic interface for CRUD generation.
    
    Args:
        model_class: SQLModel class
        module_name: Module name (e.g., "person")
        skip_existing: Skip files that exist
        include_graphql: Generate GraphQL schema
        base_path: Base path for files
        
    Returns:
        Dictionary of generated file paths
    """
    generator = CRUDGenerator(base_path)
    return generator.generate_crud(
        model_class=model_class,
        module_name=module_name,
        skip_existing=skip_existing,
        include_graphql=include_graphql
    )


if __name__ == '__main__':
    generate_crud()