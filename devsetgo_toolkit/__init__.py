# -*- coding: utf-8 -*-

"""
This is the initialization file for our library. It imports the necessary modules and functions
from various files in the library, making them accessible as package-level entities.
This allows users to import these entities directly from the package, rather than having to
navigate to the specific file where they are defined.
"""

# Importing the AsyncDatabase class from the async_database file
from .async_database import AsyncDatabase

# Importing the SchemaBase class from the base_schema file
from .base_schema import SchemaBase

# Importing the DBConfig class from the database_config file
from .database_config import DBConfig

# Importing the DatabaseOperationException and DatabaseOperations classes from the database_operations file
from .database_operations import DatabaseOperationException, DatabaseOperations

# Importing various HTTP code related entities from the http_codes file
from .http_codes import (
    ALL_HTTP_CODES,
    DELETE_CODES,
    GET_CODES,
    PATCH_CODES,
    POST_CODES,
    PUT_CODES,
    common_codes,
    generate_code_dict,
)

# Importing the create_health_router function as system_health_endpoints from the system_health_endpoints file
from .system_health_endpoints import create_health_router as system_health_endpoints
