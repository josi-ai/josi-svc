"""Base enum class with rich lookup capabilities.

Adapted from three2h-utils BaseEnum pattern.
All Josi enums inherit from this. Each member is defined as (id, description).
"""
from enum import Enum
from typing import Optional, Union, Dict, Any


class BaseEnum(Enum):

    def __init__(self, id, description, key=None, aliases=None):
        self.id = id
        self.description = description
        self.key = key if key is not None else id
        self.aliases = aliases if aliases is not None else []

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return f"{self.__class__.__name__}.{self.name}(id={self.id}, description='{self.description}')"

    @classmethod
    def from_value(cls, value):
        """Look up enum member by id or description. Raises ValueError if not found."""
        for member in cls:
            if member.id == value or member.description == value:
                return member
        raise ValueError(f"No {cls.__name__} member with value {value}")

    @classmethod
    def from_id(cls, id):
        """Look up enum member by id. Returns None if not found."""
        for member in cls:
            if member.id == id:
                return member
        return None

    @classmethod
    def from_description(cls, description):
        """Look up enum member by description. Returns None if not found."""
        for member in cls:
            if member.description == description:
                return member
        return None

    @classmethod
    def from_key(cls, key):
        """Look up enum member by member name (case-insensitive). Returns None if not found."""
        if not isinstance(key, str):
            return None
        try:
            return cls[key.upper()]
        except KeyError:
            return None

    @classmethod
    def lookup(cls, value: Union[str, int, Any]) -> Optional['BaseEnum']:
        """Flexible lookup: tries id -> description -> key. Returns None if not found."""
        if value is None:
            return None
        result = cls.from_id(value)
        if result is None:
            result = cls.from_description(value)
        if result is None:
            result = cls.from_key(value)
        return result

    @classmethod
    def lookup_with_aliases(cls, value: Union[str, Any]) -> Optional['BaseEnum']:
        """Enhanced lookup that also checks aliases (case-insensitive)."""
        if value is None:
            return None
        result = cls.lookup(value)
        if result is not None:
            return result
        if isinstance(value, str):
            value_lower = value.lower().strip()
            for member in cls:
                if member.aliases and value_lower in member.aliases:
                    return member
        return None

    @classmethod
    def name_from_id(cls, id):
        """Get enum member name from id."""
        for member in cls:
            if member.value[0] == id:
                return member.name
        return None

    @classmethod
    def description_from_id(cls, id):
        """Get description from id."""
        for member in cls:
            if member.value[0] == id:
                return member.description
        return None

    @classmethod
    def to_dict(cls) -> Dict[Any, str]:
        """Convert enum to dictionary mapping id to description."""
        return {member.id: member.description for member in cls}

    @classmethod
    def get_all_ids(cls) -> list:
        """Get list of all id values."""
        return [member.id for member in cls]

    @classmethod
    def get_all_descriptions(cls) -> list:
        """Get list of all descriptions."""
        return [member.description for member in cls]

    @classmethod
    def get_choices(cls) -> list[tuple]:
        """Get list of (id, description) tuples for form choices/dropdowns."""
        return [(member.id, member.description) for member in cls]

    @classmethod
    def to_lookup_list(cls) -> list[dict]:
        """Get list of {id, name} dicts for frontend dropdowns."""
        return [{"id": member.id, "name": member.description} for member in cls]
