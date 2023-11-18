# Base Schema Module

This module defines the base schema for database models in the application. It uses SQLAlchemy as the ORM and provides a `SchemaBase` class that all other models should inherit from. The `SchemaBase` class includes common columns that are needed for most models like `_id`, `date_created`, and `date_updated`.

## Columns

- `_id`: A unique identifier for each record. It's a string representation of a UUID.
- `date_created`: The date and time when a particular row was inserted into the table. It defaults to the current UTC time when the instance is created.
- `date_updated`: The date and time when a particular row was last updated. It defaults to the current UTC time whenever the instance is updated.

## Usage

To use this module, import it and extend the `SchemaBase` class to create new database models. Here's an example:

```python
from base_schema import SchemaBase
from sqlalchemy import Column, Integer, String

class User(SchemaBase):
    __tablename__ = 'users'

    name = Column(String, index=True)
    age = Column(Integer)

```
