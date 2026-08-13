from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Logical PostgreSQL schema for the Commerce & Cart service.
SCHEMA = "commerce_schema"


class Base(DeclarativeBase):
    """Declarative base for all ORM models in the commerce service.

    The schema is set on the MetaData so that every table lands in the
    logical service schema and unqualified ForeignKey() references
    resolve within it.
    """

    metadata = MetaData(schema=SCHEMA)
