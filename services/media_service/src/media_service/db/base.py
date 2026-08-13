from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Logical PostgreSQL schema for the Catalog & Media service.
SCHEMA = "media_schema"


class Base(DeclarativeBase):
    """Declarative base for all ORM models in the media service.

    The schema is set on the MetaData so that every table lands in the
    logical service schema and unqualified ForeignKey() references
    resolve within it.
    """

    metadata = MetaData(schema=SCHEMA)
