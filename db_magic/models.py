"""Shared table naming and integer identity conventions."""

import re

from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


class TableNameMixin:
    """Preserve the table names used by the original Magic mappings."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        name = cls.__name__
        return name[0].lower() + re.sub(
            r"([A-Z])", lambda match: "_" + match.group(0).lower(), name[1:]
        )


class Entity(TableNameMixin, DeclarativeBase):
    """Declarative base for models using an integer ``id`` primary key."""

    id: Mapped[int] = mapped_column(primary_key=True)
