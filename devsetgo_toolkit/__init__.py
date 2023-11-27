# -*- coding: utf-8 -*-

"""
This is the initialization file for our library. It imports the necessary classes and functions
from various modules within the library, making them accessible at the package level.
This allows users to import these entities directly from the package, rather than having to
import them from their specific modules.
"""

# Import the AsyncDatabase class from the async_database module
from .database.async_database import AsyncDatabase

# Import the SchemaBase class from the base_schema module
from .database.base_schema import SchemaBase

# Import the DBConfig class from the database_config module
from .database.database_config import DBConfig

# Import the DatabaseOperations class from the database_operations module
from .database.database_operations import DatabaseOperations

# Import various HTTP code related entities from the http_codes module
from .endpoints.http_codes import (
    ALL_HTTP_CODES,
    DELETE_CODES,
    GET_CODES,
    PATCH_CODES,
    POST_CODES,
    PUT_CODES,
    common_codes,
    generate_code_dict,
)

# Import the create_health_router function as system_health_endpoints from the system_health_endpoints module
from .endpoints.system_health_endpoints import (
    create_health_router as system_health_endpoints,
)
