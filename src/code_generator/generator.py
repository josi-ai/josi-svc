"""
CRUD generator implementation.
"""
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from jinja2 import Environment, FileSystemLoader, Template
import inflection
from sqlmodel import SQLModel
import inspect


class CRUDGenerator:
    """
    Generates CRUD operations for SQLModel models.
    
    This generator creates:
    - REST API controllers with standard CRUD endpoints
    - Service layer with business logic
    - Repository layer for database operations
    - GraphQL schema and resolvers
    - All with proper type hints and documentation
    """
    
    def __init__(self, base_path: str = "src/josi"):
        self.base_path = Path(base_path)
        self.template_dir = Path(__file__).parent / "templates"
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.env.filters['snake_case'] = inflection.underscore
        self.env.filters['camel_case'] = inflection.camelize
        self.env.filters['plural'] = inflection.pluralize
        self.env.filters['singular'] = inflection.singularize
        self.env.filters['title_case'] = lambda x: inflection.titleize(x)
    
    def generate_crud(
        self,
        model_class: type[SQLModel],
        module_name: str,
        skip_existing: bool = True,
        include_graphql: bool = True
    ) -> Dict[str, str]:
        """
        Generate CRUD operations for a model.
        
        Args:
            model_class: SQLModel class to generate CRUD for
            module_name: Module name (e.g., "person", "chart")
            skip_existing: Skip files that already exist
            include_graphql: Generate GraphQL schema
            
        Returns:
            Dictionary of generated file paths
        """
        # Extract model information
        model_info = self._extract_model_info(model_class)
        model_info['module_name'] = module_name
        
        generated_files = {}
        
        # Generate controller
        controller_path = self._generate_controller(model_info, skip_existing)
        if controller_path:
            generated_files['controller'] = controller_path
        
        # Generate service
        service_path = self._generate_service(model_info, skip_existing)
        if service_path:
            generated_files['service'] = service_path
        
        # Generate repository
        repository_path = self._generate_repository(model_info, skip_existing)
        if repository_path:
            generated_files['repository'] = repository_path
        
        # Generate GraphQL schema if requested
        if include_graphql:
            graphql_path = self._generate_graphql(model_info, skip_existing)
            if graphql_path:
                generated_files['graphql'] = graphql_path
        
        # Update __init__.py files
        self._update_init_files(model_info)
        
        return generated_files
    
    def _extract_model_info(self, model_class: type[SQLModel]) -> Dict[str, Any]:
        """Extract information from the model class."""
        fields = {}
        relationships = []
        primary_key = None
        
        # Get fields from model
        for field_name, field_info in model_class.__fields__.items():
            field_type = field_info.outer_type_
            is_optional = False
            
            # Check if optional
            if hasattr(field_type, '__origin__') and field_type.__origin__ is type(Optional):
                is_optional = True
                field_type = field_type.__args__[0]
            
            # Check for primary key
            field_def = getattr(model_class, field_name, None)
            if hasattr(field_def, 'primary_key') and field_def.primary_key:
                primary_key = field_name
            
            # Check for relationships
            if hasattr(field_def, 'foreign_key'):
                relationships.append({
                    'name': field_name,
                    'type': field_type.__name__ if hasattr(field_type, '__name__') else str(field_type),
                    'foreign_key': field_def.foreign_key
                })
            
            fields[field_name] = {
                'name': field_name,
                'type': field_type.__name__ if hasattr(field_type, '__name__') else str(field_type),
                'optional': is_optional,
                'default': field_info.default if field_info.default is not None else None
            }
        
        return {
            'model_name': model_class.__name__,
            'table_name': model_class.__tablename__ if hasattr(model_class, '__tablename__') else inflection.underscore(model_class.__name__),
            'fields': fields,
            'relationships': relationships,
            'primary_key': primary_key or 'id',
            'has_organization': 'organization_id' in fields,
            'has_soft_delete': 'is_deleted' in fields
        }
    
    def _generate_controller(self, model_info: Dict[str, Any], skip_existing: bool) -> Optional[str]:
        """Generate REST API controller."""
        template = self.env.get_template('controller.py.j2')
        content = template.render(**model_info)
        
        # Determine file path
        controller_name = f"{model_info['module_name']}_controller.py"
        file_path = self.base_path / "api" / "v1" / "controllers" / controller_name
        
        if skip_existing and file_path.exists():
            return None
        
        # Create directory if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        file_path.write_text(content)
        return str(file_path)
    
    def _generate_service(self, model_info: Dict[str, Any], skip_existing: bool) -> Optional[str]:
        """Generate service layer."""
        template = self.env.get_template('service.py.j2')
        content = template.render(**model_info)
        
        service_name = f"{model_info['module_name']}_service.py"
        file_path = self.base_path / "services" / service_name
        
        if skip_existing and file_path.exists():
            return None
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return str(file_path)
    
    def _generate_repository(self, model_info: Dict[str, Any], skip_existing: bool) -> Optional[str]:
        """Generate repository layer."""
        template = self.env.get_template('repository.py.j2')
        content = template.render(**model_info)
        
        repository_name = f"{model_info['module_name']}_repository.py"
        file_path = self.base_path / "repositories" / repository_name
        
        if skip_existing and file_path.exists():
            return None
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return str(file_path)
    
    def _generate_graphql(self, model_info: Dict[str, Any], skip_existing: bool) -> Optional[str]:
        """Generate GraphQL schema."""
        template = self.env.get_template('graphql_schema.py.j2')
        content = template.render(**model_info)
        
        schema_name = f"{model_info['module_name']}_schema.py"
        file_path = self.base_path / "graphql" / "schema" / schema_name
        
        if skip_existing and file_path.exists():
            return None
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
        return str(file_path)
    
    def _update_init_files(self, model_info: Dict[str, Any]):
        """Update __init__.py files to include new modules."""
        # Update controllers __init__.py
        controllers_init = self.base_path / "api" / "v1" / "controllers" / "__init__.py"
        if controllers_init.exists():
            content = controllers_init.read_text()
            import_line = f"from .{model_info['module_name']}_controller import router as {model_info['module_name']}_router\n"
            if import_line not in content:
                controllers_init.write_text(content + import_line)