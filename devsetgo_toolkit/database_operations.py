# -*- coding: utf-8 -*-

"""
This Python module, database_operations.py, provides a class DatabaseOperations for managing asynchronous database operations using SQLAlchemy.

The DatabaseOperations class provides methods for executing various types of database operations, including count queries, fetch queries, record insertions, updates, and deletions. It uses an instance of the AsyncDatabase class to perform these operations asynchronously.

The module imports necessary modules and packages from sqlalchemy for database operations and error handling. It also imports AsyncDatabase from the local module async_database.

The DatabaseOperations class has the following methods:

__init__: Initializes a new instance of the DatabaseOperations class.
count_query: Executes a count query and returns the result.
get_query: Executes a fetch query and returns the result.
get_queries: Executes multiple fetch queries and returns the results.
insert_one: Adds a single record to the database.
insert_many: Adds multiple records to the database.
update_one: Updates a single record in the database.
delete_one: Deletes a single record from the database.
Each method is designed to handle exceptions and log errors and information messages using the logging module.

This module is designed to be used in an asynchronous context and requires Python 3.7+.
"""

import logging as logger  # Importing logging module for logging
import time  # Importing time module to work with times

# Importing asynccontextmanager from contextlib for creating context managers

# Importing Dict and List from typing for type hinting
from typing import Dict, List

# Importing MetaData and func from sqlalchemy for database operations
from sqlalchemy import func

# Importing specific exceptions from sqlalchemy for error handling
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Importing AsyncSession and create_async_engine from sqlalchemy for asynchronous database operations

# Importing select from sqlalchemy for making select queries
from sqlalchemy.future import select

# Importing declarative_base and sessionmaker from sqlalchemy for ORM operations

# Importing AsyncDatabase class from local module async_database
from .async_database import AsyncDatabase


class DatabaseOperations:
    """
        The DatabaseOperations class provides methods for executing various types of database operations asynchronously using SQLAlchemy.

    This class is initialized with an instance of the AsyncDatabase class, which is used for performing the actual database operations.

    The class provides the following methods:

    __init__: Initializes a new instance of the DatabaseOperations class.
    count_query: Executes a count query and returns the result.
    get_query: Executes a fetch query and returns the result.
    get_queries: Executes multiple fetch queries and returns the results.
    insert_one: Adds a single record to the database.
    insert_many: Adds multiple records to the database.
    update_one: Updates a single record in the database.
    delete_one: Deletes a single record from the database.
    Each method is designed to handle exceptions and log errors and information messages using the logging module.

    This class is designed to be used in an asynchronous context and requires Python 3.7+.
    """

    def __init__(self, async_db: AsyncDatabase):
        """
        Initializes a new instance of the DatabaseOperations class.

        This method takes an instance of the AsyncDatabase class as input and stores it in the async_db attribute for later use in other methods.

        Parameters:
        async_db (AsyncDatabase): An instance of the AsyncDatabase class for performing asynchronous database operations.
        """
        # Store the AsyncDatabase instance in the async_db attribute
        logger.debug("Initializing DatabaseOperations instance")
        self.async_db = async_db
        logger.info("DatabaseOperations instance initialized successfully")

    async def count_query(self, query):
        """
        Executes a count query and returns the result.

        This method takes a SQLAlchemy query as input, executes it against the database to count the number of matching records, and returns the count. If an error occurs during the operation, it logs the error and returns a dictionary containing the error details.

        Parameters:
        query (sqlalchemy.sql.selectable.Select): The SQLAlchemy query to execute.

        Returns:
        int or dict: The count of matching records if the operation is successful, otherwise a dictionary containing the error details.
        """
        logger.debug("Starting count_query operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Execute the count query
                logger.debug(f"Executing count query: {query}")
                result = await session.execute(select(func.count()).select_from(query))
                count = result.scalar()
                logger.info(f"Count query executed successfully. Result: {count}")
                return count
        except SQLAlchemyError as ex:
            # Log and handle SQLAlchemyError
            logger.error(f"SQLAlchemyError occurred during count query execution: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Log and handle general exceptions
            logger.error(f"Exception occurred during count query execution: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "General Exception", "details": error_only}

    async def get_query(self, query, limit=500, offset=0):
        """
        Executes a fetch query and returns the result.

        This method takes a SQL query, executes it against the database to fetch the matching records, and returns the records. It also supports pagination through the limit and offset parameters.

        Parameters:
        query (str): The SQL query to execute.
        limit (int, optional): The maximum number of records to return. Defaults to 500.
        offset (int, optional): The number of records to skip before starting to fetch the records. Defaults to 0.

        Returns:
        list: The list of matching records.
        """
        logger.debug("Starting get_query operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Execute the fetch query with the given limit and offset
                logger.debug(f"Fetch Query: {query}")
                result = await session.execute(query.limit(limit).offset(offset))
                data = result.scalars().all()
                logger.info(f"Fetch Result: {data}")
                return data
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on fetch query: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}

        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during get query: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def get_queries(self, queries: Dict[str, str], limit=500, offset=0):
        """
        Executes multiple fetch queries and returns the results.

        This method takes a dictionary of SQL queries, executes each query against the database to fetch the matching records, and returns a dictionary of results. Each key in the result dictionary corresponds to a query name, and the value is a list of matching records for that query. The method also supports pagination through the limit and offset parameters.

        Parameters:
        queries (Dict[str, str]): A dictionary where the key is the query name and the value is the SQL query to execute.
        limit (int, optional): The maximum number of records to return for each query. Defaults to 500.
        offset (int, optional): The number of records to skip before starting to fetch the records for each query. Defaults to 0.

        Returns:
        Dict[str, list]: A dictionary where the key is the query name and the value is a list of matching records.
        """
        logger.debug("Starting get_queries operation")
        try:
            results = {}
            async with self.async_db.get_db_session() as session:
                # Execute each fetch query with the given limit and offset
                logger.debug(f"Fetch Queries: {queries}")
                for query_name, query in queries.items():
                    logger.debug(f"Fetch Query: {query}")
                    result = await session.execute(query.limit(limit).offset(offset))
                    data = result.scalars().all()
                    logger.info(f"Fetch Result: {data}")
                    results[query_name] = data
            return results
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on fetch queries: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}

        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during get queries: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def insert_one(self, record):
        """
        Adds a single record to the database.

        This method takes a record, adds it to the database session, and commits the session. If the operation is successful, it returns the record. If an error occurs during the operation, it raises a DatabaseOperationException with detailed information about the error.

        Parameters:
        record (dict): The record to add to the database.

        Returns:
        dict: The record that was added to the database.

        Raises:
        DatabaseOperationException: If an error occurs during the database operation.
        """
        logger.debug("Starting insert_one operation")
        try:
            async with self.async_db.get_db_session() as session:
                # Add the record to the session and commit
                logger.debug(f"Record insert: {record}")
                session.add(record)
                await session.commit()
            logger.info(f"Record operation was successful: {record}.")
            return record
        except IntegrityError as ex:
            # Handle IntegrityError
            logger.error(f"IntegrityError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "IntegrityError", "details": error_only}
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on record: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during insert one: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def insert_many(self, records: List[dict]):
        """
        Adds multiple records to the database.

        This method takes a list of records, adds each record to the database session, and commits the session. If the operation is successful, it returns the list of records. If an error occurs during the operation, it raises a DatabaseOperationException with detailed information about the error.

        Parameters:
        records (List[dict]): The list of records to add to the database. Each record is a dictionary representing a row to be inserted into the database.

        Returns:
        List[dict]: The list of records that were added to the database.

        Raises:
        DatabaseOperationException: If an error occurs during the database operation.
        """
        logger.debug("Starting insert_many operation")
        try:
            t0 = time.time()  # Record the start time of the operation
            async with self.async_db.get_db_session() as session:
                # Add all the records to the session and commit
                logger.debug(f"Adding {len(records)} records to session")
                session.add_all(records)  # Add all records to the session
                await session.commit()  # Commit the session to save the records to the database

                num_records = len(records)  # Get the number of records added
                t1 = time.time() - t0  # Calculate the time taken for the operation
                logger.info(
                    f"Record operations were successful. {num_records} records were created in {t1:.4f} seconds."
                )
                return records  # Return the list of records added
        except IntegrityError as ex:
            # Handle IntegrityError, which occurs when a database constraint is violated
            logger.error(f"IntegrityError on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "IntergityError", "details": error_only}

        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError, which is a base class for all SQLAlchemy exceptions
            logger.error(f"SQLAlchemyError on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception Failed to perform operations on records: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "General Exception", "details": error_only}

    async def update_one(self, table, record_id: str, new_values: dict):
        non_updatable_fields = ["id", "date_created"]

        logger.debug(
            f"Starting update_one operation for record_id: {record_id} in table: {table.__name__}"
        )

        try:
            async with self.async_db.get_db_session() as session:
                # Fetch the record to be updated
                logger.debug(f"Fetching record with id: {record_id}")
                record = await session.get(table, record_id)
                if not record:
                    logger.error(f"No record found with id: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with id {record_id}",
                    }

                # Update the record with new values
                logger.debug(f"Updating record with new values: {new_values}")
                for key, value in new_values.items():
                    if key not in non_updatable_fields:
                        logger.debug(f"Updating field: {key} with value: {value}")
                        setattr(record, key, value)
                    else:
                        logger.debug(f"Skipping non-updatable field: {key}")

                # Commit the changes
                logger.debug(f"Committing changes to the database for ID: {record_id}")
                await session.commit()

                logger.info(
                    f"Record update was successful: ID: {record_id}, Record: {record}"
                )
                return record
        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on update: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}
        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during update: {ex}")
            return {"error": "General Exception", "details": str(ex)}

    async def delete_one(self, table, record_id):
        try:
            async with self.async_db.get_db_session() as session:
                # Fetch the record to be deleted
                record = await session.get(table, record_id)

                # If the record doesn't exist, return None
                if not record:
                    logger.error(f"No record found with id: {record_id}")
                    return {
                        "error": "Record not found",
                        "details": f"No record found with id {record_id}",
                    }

                # Delete the record
                await session.delete(record)

                # Commit the changes
                await session.commit()

                return {"success": "Record deleted successfully"}

        except SQLAlchemyError as ex:
            # Handle SQLAlchemyError
            logger.error(f"SQLAlchemyError on delete: {ex}")
            error_only = str(ex).split("[SQL:")[0]
            return {"error": "SQLAlchemyError", "details": error_only}

        except Exception as ex:
            # Handle general exceptions
            logger.error(f"Exception occurred during delete one: {ex}")
            return {"error": "General Exception", "details": str(ex)}
