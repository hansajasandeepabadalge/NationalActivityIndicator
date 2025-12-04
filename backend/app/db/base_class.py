"""SQLAlchemy Base class for all models - Integrated"""
from typing import Any
from sqlalchemy.orm import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Base class for SQLAlchemy models.
    Auto-generates __tablename__ from class name if not specified.
    """
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate __tablename__ automatically from class name."""
        return cls.__name__.lower()
